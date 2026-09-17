from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message content cannot be empty or whitespace only.")
        if len(stripped) > 5000:
            raise ValueError("Message content cannot exceed 5000 characters.")
        return stripped


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: Optional[int] = None
    sender_id: int
    recipient_id: int
    subject: Optional[str] = None
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


class ParticipantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    trust_score: int = 50
    is_verified: bool = False


class ConversationCreate(BaseModel):
    recipient_id: int
    project_id: Optional[int] = None
    sponsorship_request_id: Optional[int] = None
    commitment_id: Optional[int] = None
    initial_message: Optional[str] = None

    @field_validator("initial_message")
    @classmethod
    def validate_initial_message(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                return None
            if len(stripped) > 5000:
                raise ValueError("Initial message cannot exceed 5000 characters.")
            return stripped
        return v


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    participant1_id: int
    participant2_id: int
    other_participant: ParticipantSummary
    project_id: Optional[int] = None
    project_title: Optional[str] = None
    sponsorship_request_id: Optional[int] = None
    commitment_id: Optional[int] = None
    commitment_status: Optional[str] = None
    compatibility_score: Optional[int] = None
    last_message_at: datetime
    last_message_preview: Optional[str] = None
    unread_count: int = 0
    created_at: datetime


class ConversationDetailRead(ConversationRead):
    messages: List[MessageRead] = []


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str
    type: str
    link: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: List[NotificationRead]
    total: int
    unread_count: int


class NotificationPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    in_app_messages: bool = True
    in_app_sponsorship_requests: bool = True
    in_app_commitments: bool = True
    in_app_milestones: bool = True
    in_app_follow_ups: bool = True
    in_app_trust_score: bool = True
    email_notifications: bool = False
    created_at: datetime
    updated_at: datetime


class NotificationPreferenceUpdate(BaseModel):
    in_app_messages: Optional[bool] = None
    in_app_sponsorship_requests: Optional[bool] = None
    in_app_commitments: Optional[bool] = None
    in_app_milestones: Optional[bool] = None
    in_app_follow_ups: Optional[bool] = None
    in_app_trust_score: Optional[bool] = None
    email_notifications: Optional[bool] = None


class UnreadCountsResponse(BaseModel):
    unread_messages: int = 0
    unread_notifications: int = 0
