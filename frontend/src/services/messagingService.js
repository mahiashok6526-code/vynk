import { apiRequest } from './api';

export const messagingService = {
  /**
   * List conversations for the authenticated user
   */
  async getConversations(limit = 50, offset = 0) {
    return apiRequest(`/messages/conversations?limit=${limit}&offset=${offset}`);
  },

  /**
   * Initiate or retrieve an authorized conversation thread
   */
  async createOrGetConversation(payload) {
    return apiRequest('/messages/conversations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Retrieve conversation detail with chronological message history
   */
  async getConversationDetail(conversationId, limit = 100, offset = 0) {
    return apiRequest(`/messages/conversations/${conversationId}?limit=${limit}&offset=${offset}`);
  },

  /**
   * Send a new message in an existing conversation
   */
  async sendMessage(conversationId, content) {
    return apiRequest(`/messages/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  },

  /**
   * Explicitly mark all incoming unread messages as read
   */
  async markConversationRead(conversationId) {
    return apiRequest(`/messages/conversations/${conversationId}/read`, {
      method: 'PATCH',
    });
  },

  /**
   * Fetch total unread message count
   */
  async getUnreadMessageCount() {
    return apiRequest('/messages/unread-count');
  },
};
