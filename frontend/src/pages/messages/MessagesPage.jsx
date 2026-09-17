import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { messagingService } from '../../services/messagingService';
import { TrustScoreBadge } from '../../components/common/TrustScoreBadge';
import { Badge } from '../../components/common/Badge';

export function MessagesPage() {
  const { user: currentUser } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [isLoadingActive, setIsLoadingActive] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  const messagesEndRef = useRef(null);
  const composerRef = useRef(null);

  // Target conversation ID from URL query param
  const queryConvId = searchParams.get('conversation_id');
  const queryRecipientId = searchParams.get('recipient_id');
  const queryProjectId = searchParams.get('project_id');

  // 1. Initial load of conversation list
  const loadConversations = async (selectId = null) => {
    try {
      setErrorMessage(null);
      const list = await messagingService.getConversations();
      setConversations(list || []);

      // If specific ID requested or passed
      const targetId = selectId || (queryConvId ? parseInt(queryConvId, 10) : null);
      if (targetId) {
        setActiveConversationId(targetId);
      } else if (!activeConversationId && list && list.length > 0) {
        setActiveConversationId(list[0].id);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to load conversations.');
    } finally {
      setIsLoadingList(false);
    }
  };

  useEffect(() => {
    // If recipient_id was provided via query param (e.g. from a profile or project card)
    if (queryRecipientId && !queryConvId) {
      const initFromQuery = async () => {
        try {
          setIsLoadingActive(true);
          const newConv = await messagingService.createOrGetConversation({
            recipient_id: parseInt(queryRecipientId, 10),
            project_id: queryProjectId ? parseInt(queryProjectId, 10) : undefined,
          });
          setSearchParams({ conversation_id: newConv.id });
          await loadConversations(newConv.id);
        } catch (err) {
          setErrorMessage(err.message || 'Could not initiate conversation. Active relationship required.');
          setIsLoadingActive(false);
          await loadConversations();
        }
      };
      initFromQuery();
    } else {
      loadConversations();
    }
  }, [queryConvId, queryRecipientId]);

  // 2. Fetch active conversation details & messages
  const loadActiveConversation = async (silent = false) => {
    if (!activeConversationId) return;
    if (!silent) setIsLoadingActive(true);

    try {
      const detail = await messagingService.getConversationDetail(activeConversationId);
      setActiveConversation(detail);

      // Trigger global navbar unread refresh
      window.dispatchEvent(new CustomEvent('vynk:refresh-unread'));

      // Update unread count in local list
      setConversations((prev) =>
        prev.map((c) => (c.id === activeConversationId ? { ...c, unread_count: 0 } : c))
      );
    } catch (err) {
      if (!silent) setErrorMessage(err.message || 'Failed to load message history.');
    } finally {
      if (!silent) setIsLoadingActive(false);
    }
  };

  useEffect(() => {
    if (activeConversationId) {
      loadActiveConversation(false);
    }
  }, [activeConversationId]);

  // 3. REST Polling: active conversation polled approximately every 4 seconds
  useEffect(() => {
    if (!activeConversationId) return;

    const interval = setInterval(() => {
      loadActiveConversation(true);
    }, 4000);

    return () => clearInterval(interval);
  }, [activeConversationId]);

  // 4. Auto-scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeConversation?.messages]);

  // 5. Send Message
  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    const clean = messageInput.trim();
    if (!clean || !activeConversationId || isSending) return;

    if (clean.length > 5000) {
      setErrorMessage('Message exceeds maximum length of 5,000 characters.');
      return;
    }

    setIsSending(true);
    setErrorMessage(null);

    try {
      const newMsg = await messagingService.sendMessage(activeConversationId, clean);
      setMessageInput('');

      // Immediately append message to active conversation for instant feedback
      setActiveConversation((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          messages: [...prev.messages, newMsg],
          last_message_at: newMsg.created_at,
          last_message_preview: clean.slice(0, 100),
        };
      });

      // Update sidebar conversation preview
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId
            ? {
                ...c,
                last_message_at: newMsg.created_at,
                last_message_preview: clean.slice(0, 100),
              }
            : c
        )
      );

      // Re-focus composer
      if (composerRef.current) {
        composerRef.current.focus();
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to deliver message.');
    } finally {
      setIsSending(false);
    }
  };

  // 6. Filter conversations
  const filteredConversations = conversations.filter((c) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const nameMatch = c.other_participant?.full_name?.toLowerCase().includes(q);
    const projectMatch = c.project_title?.toLowerCase().includes(q);
    return nameMatch || projectMatch;
  });

  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className="container" style={{ padding: '24px 16px', minHeight: 'calc(100vh - var(--header-height) - 80px)' }}>
      {/* Alert / Error Banner */}
      {errorMessage && (
        <div
          style={{
            marginBottom: 16,
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            color: '#fda4af',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: 14,
          }}
        >
          <span>{errorMessage}</span>
          <button
            onClick={() => setErrorMessage(null)}
            style={{ background: 'none', border: 'none', color: '#fda4af', cursor: 'pointer', fontSize: 16 }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Two-Pane Layout */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '320px 1fr',
          gap: 20,
          height: '78vh',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          boxShadow: 'var(--shadow-md)',
        }}
        id="messages-container"
      >
        {/* LEFT SIDEBAR: Conversation Threads List */}
        <div
          style={{
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'rgba(13, 18, 29, 0.65)',
          }}
        >
          {/* Sidebar Header */}
          <div style={{ padding: '18px 16px 12px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Messages</h2>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {conversations.length} {conversations.length === 1 ? 'chat' : 'chats'}
              </span>
            </div>

            {/* Search filter */}
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search conversations..."
                className="input"
                style={{
                  width: '100%',
                  height: 36,
                  fontSize: 13,
                  backgroundColor: 'var(--bg-surface)',
                  paddingLeft: 34,
                }}
                id="search-conversations-input"
              />
              <span
                style={{
                  position: 'absolute',
                  left: 10,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                  fontSize: 14,
                  pointerEvents: 'none',
                }}
              >
                🔍
              </span>
            </div>
          </div>

          {/* Conversation List Scroll Area */}
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {isLoadingList ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
                <div className="spinner" style={{ width: 28, height: 28 }} />
              </div>
            ) : filteredConversations.length === 0 ? (
              <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
                {searchQuery ? 'No matching conversations found.' : 'No conversations yet. Connect via projects or sponsors.'}
              </div>
            ) : (
              filteredConversations.map((conv) => {
                const isSelected = conv.id === activeConversationId;
                const other = conv.other_participant;
                return (
                  <div
                    key={conv.id}
                    onClick={() => {
                      setActiveConversationId(conv.id);
                      setSearchParams({ conversation_id: conv.id });
                    }}
                    style={{
                      padding: '14px 16px',
                      cursor: 'pointer',
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'transparent',
                      borderLeft: isSelected ? '3px solid var(--brand-cyan)' : '3px solid transparent',
                      transition: 'background-color 0.15s ease',
                    }}
                    className="conversation-item"
                    id={`conversation-item-${conv.id}`}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                      {/* Avatar */}
                      <div
                        style={{
                          width: 42,
                          height: 42,
                          borderRadius: '50%',
                          backgroundColor: 'var(--bg-surface-elevated)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: 16,
                          color: other?.role === 'sponsor' ? 'var(--brand-emerald)' : 'var(--brand-cyan)',
                          flexShrink: 0,
                          overflow: 'hidden',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        {other?.avatar_url ? (
                          <img src={other.avatar_url} alt={other.full_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                          other?.full_name?.charAt(0) || 'U'
                        )}
                      </div>

                      {/* Content */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 2 }}>
                          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {other?.full_name}
                          </span>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', flexShrink: 0 }}>
                            {formatTime(conv.last_message_at)}
                          </span>
                        </div>

                        {/* Badges / Context Row */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, flexWrap: 'wrap' }}>
                          <Badge variant={other?.role === 'sponsor' ? 'emerald' : 'cyan'} size="sm">
                            {other?.role}
                          </Badge>
                          {other?.trust_score && (
                            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                              TS {other.trust_score}
                            </span>
                          )}
                          {conv.project_title && (
                            <span
                              style={{
                                fontSize: 11,
                                padding: '1px 6px',
                                borderRadius: 4,
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                color: 'var(--text-secondary)',
                                maxWidth: 110,
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {conv.project_title}
                            </span>
                          )}
                        </div>

                        {/* Last Message Preview */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <p
                            style={{
                              fontSize: 12,
                              color: conv.unread_count > 0 ? 'var(--text-primary)' : 'var(--text-muted)',
                              fontWeight: conv.unread_count > 0 ? 600 : 400,
                              margin: 0,
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {conv.last_message_preview || 'No messages yet'}
                          </p>
                          {conv.unread_count > 0 && (
                            <span
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                minWidth: 18,
                                height: 18,
                                padding: '0 5px',
                                borderRadius: 999,
                                backgroundColor: 'var(--brand-cyan)',
                                color: 'var(--text-inverse)',
                                fontSize: 10,
                                fontWeight: 700,
                                marginLeft: 6,
                                flexShrink: 0,
                              }}
                            >
                              {conv.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* RIGHT PANE: Active Conversation View */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: 'var(--bg-primary)' }}>
          {isLoadingActive ? (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div className="spinner" style={{ width: 32, height: 32 }} />
            </div>
          ) : !activeConversation ? (
            <div
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-muted)',
                padding: 32,
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: 42, marginBottom: 12 }}>💬</div>
              <h3 style={{ fontSize: 18, color: 'var(--text-primary)', marginBottom: 6 }}>Select a Conversation</h3>
              <p style={{ fontSize: 14, maxWidth: 360 }}>
                Choose a conversation from the sidebar or initiate discussions with verified founders and sponsors.
              </p>
            </div>
          ) : (
            <>
              {/* Active Conversation Header */}
              <div
                style={{
                  padding: '14px 20px',
                  borderBottom: '1px solid var(--border-subtle)',
                  backgroundColor: 'rgba(18, 25, 39, 0.7)',
                  backdropFilter: 'blur(8px)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 12,
                }}
                id="conversation-header"
              >
                {/* Participant Details */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: '50%',
                      backgroundColor: 'var(--bg-surface-elevated)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontSize: 18,
                      color: activeConversation.other_participant?.role === 'sponsor' ? 'var(--brand-emerald)' : 'var(--brand-cyan)',
                      overflow: 'hidden',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    {activeConversation.other_participant?.avatar_url ? (
                      <img
                        src={activeConversation.other_participant.avatar_url}
                        alt={activeConversation.other_participant.full_name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : (
                      activeConversation.other_participant?.full_name?.charAt(0) || 'U'
                    )}
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                        {activeConversation.other_participant?.full_name}
                      </span>
                      {activeConversation.other_participant?.is_verified && (
                        <span style={{ color: 'var(--brand-cyan)', fontSize: 14 }} title="Verified Vynk Member">
                          ✓
                        </span>
                      )}
                      <Badge variant={activeConversation.other_participant?.role === 'sponsor' ? 'emerald' : 'cyan'} size="sm">
                        {activeConversation.other_participant?.role}
                      </Badge>
                    </div>
                    {activeConversation.other_participant?.username && (
                      <Link
                        to={`/p/${activeConversation.other_participant.username}`}
                        style={{ fontSize: 12, color: 'var(--brand-cyan)', textDecoration: 'none' }}
                      >
                        @{activeConversation.other_participant.username} • View Profile
                      </Link>
                    )}
                  </div>
                </div>

                {/* Context Badges: Trust Score, Compatibility Score, Project Link, Commitment Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                  {activeConversation.other_participant?.trust_score !== undefined && (
                    <TrustScoreBadge
                      score={activeConversation.other_participant.trust_score}
                      size="sm"
                      showLabel={true}
                    />
                  )}

                  {activeConversation.compatibility_score !== null && (
                    <div
                      style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'rgba(99, 102, 241, 0.15)',
                        border: '1px solid rgba(99, 102, 241, 0.35)',
                        color: '#a5b4fc',
                        fontSize: 12,
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                      }}
                      title="AI Compatibility Match Score"
                    >
                      <span>⚡</span>
                      <span>{activeConversation.compatibility_score}% Match</span>
                    </div>
                  )}

                  {activeConversation.project_id && (
                    <Link
                      to={`/projects/${activeConversation.project_id}`}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--text-secondary)',
                        fontSize: 12,
                        fontWeight: 500,
                        textDecoration: 'none',
                      }}
                      title="Associated Project"
                    >
                      🚀 {activeConversation.project_title || 'Project Context'}
                    </Link>
                  )}

                  {activeConversation.commitment_id && (
                    <Link
                      to={`/commitments/${activeConversation.commitment_id}`}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'rgba(16, 185, 129, 0.12)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        color: 'var(--brand-emerald)',
                        fontSize: 12,
                        fontWeight: 600,
                        textDecoration: 'none',
                      }}
                      title="Sponsorship Commitment"
                    >
                      💼 {activeConversation.commitment_status?.toUpperCase() || 'COMMITMENT'}
                    </Link>
                  )}
                </div>
              </div>

              {/* Message History Area */}
              <div
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '20px 24px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 16,
                }}
                id="message-history-list"
              >
                {activeConversation.messages.length === 0 ? (
                  <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <div style={{ fontSize: 32, marginBottom: 8 }}>👋</div>
                    <p style={{ fontSize: 14 }}>Start the conversation by typing your message below.</p>
                  </div>
                ) : (
                  activeConversation.messages.map((msg) => {
                    const isMine = msg.sender_id === currentUser?.id;
                    return (
                      <div
                        key={msg.id}
                        style={{
                          display: 'flex',
                          justifyContent: isMine ? 'flex-end' : 'flex-start',
                          alignItems: 'flex-end',
                          gap: 8,
                        }}
                        className={`message-row ${isMine ? 'message-mine' : 'message-theirs'}`}
                      >
                        {!isMine && (
                          <div
                            style={{
                              width: 28,
                              height: 28,
                              borderRadius: '50%',
                              backgroundColor: 'var(--bg-surface-elevated)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 12,
                              fontWeight: 700,
                              color: 'var(--brand-cyan)',
                              flexShrink: 0,
                            }}
                          >
                            {activeConversation.other_participant?.full_name?.charAt(0) || 'U'}
                          </div>
                        )}

                        <div
                          style={{
                            maxWidth: '68%',
                            padding: '12px 16px',
                            borderRadius: isMine ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                            backgroundColor: isMine ? 'var(--brand-cyan)' : 'var(--bg-surface)',
                            color: isMine ? 'var(--text-inverse)' : 'var(--text-primary)',
                            border: isMine ? 'none' : '1px solid var(--border-subtle)',
                            boxShadow: isMine ? 'var(--shadow-glow-cyan)' : 'var(--shadow-sm)',
                            wordBreak: 'break-word',
                          }}
                        >
                          {/* Message Content rendered safely through React JSX text nodes to prevent XSS */}
                          <div style={{ fontSize: 14, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                            {msg.content}
                          </div>

                          {/* Footer: Timestamp and Read Status */}
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-end',
                              gap: 4,
                              marginTop: 4,
                              fontSize: 10,
                              color: isMine ? 'rgba(7, 9, 14, 0.7)' : 'var(--text-muted)',
                            }}
                          >
                            <span>
                              {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            {isMine && (
                              <span title={msg.is_read ? 'Read' : 'Delivered'}>
                                {msg.is_read ? '✓✓' : '✓'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Composer Area */}
              <div
                style={{
                  padding: '14px 20px',
                  borderTop: '1px solid var(--border-subtle)',
                  backgroundColor: 'var(--bg-surface)',
                }}
              >
                <form onSubmit={handleSendMessage} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12 }}>
                    <textarea
                      ref={composerRef}
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="Write a message... (Press Enter to send, Shift+Enter for new line)"
                      style={{
                        flex: 1,
                        minHeight: 44,
                        maxHeight: 120,
                        padding: '10px 14px',
                        borderRadius: 'var(--radius-md)',
                        backgroundColor: 'var(--bg-primary)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--text-primary)',
                        fontSize: 14,
                        fontFamily: 'inherit',
                        resize: 'none',
                        outline: 'none',
                      }}
                      id="message-composer-input"
                      rows={1}
                    />
                    <button
                      type="submit"
                      disabled={isSending || !messageInput.trim()}
                      className="btn btn-primary"
                      style={{
                        height: 44,
                        padding: '0 20px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        fontWeight: 600,
                      }}
                      id="message-send-btn"
                    >
                      {isSending ? (
                        <div className="spinner" style={{ width: 16, height: 16 }} />
                      ) : (
                        <>
                          <span>Send</span>
                          <span>➤</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Character Counter & Notice */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Strict relationship authorization active • Messages are immutable
                    </span>
                    <span
                      style={{
                        color: messageInput.length > 4500 ? 'var(--brand-rose)' : 'var(--text-muted)',
                        fontWeight: messageInput.length > 4500 ? 700 : 400,
                      }}
                    >
                      {messageInput.length} / 5,000
                    </span>
                  </div>
                </form>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default MessagesPage;
