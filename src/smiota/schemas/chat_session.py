"""Schemas for Standardized Event Envelopes, Chat Sessions, and Polymorphic Message Payloads."""
from datetime import UTC, datetime
from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field, model_validator

MessageType = str


class MessageSender(BaseModel):
    """Actor identity attribution for conversation messages."""
    role: Literal["user", "assistant", "system"] = Field("user", description="Actor classification")
    name: str = Field("User", description="Display name of user, agent, or service")
    id: str | None = Field(None, description="Unique identifier (e.g. resident ID or agent key)")
    user: dict[str, Any] | None = Field(default=None, description="User necessary information object")
    user_info: dict[str, Any] | None = Field(default=None, description="Detailed user information object")


class UserMessageContent(BaseModel):
    """Content payload for resident queries."""
    text: str = Field(..., description="Message text from the resident")
    attachments: list[dict[str, Any]] = Field(default_factory=list, description="Optional images/files")


class AgentCardContent(BaseModel):
    """Content payload for rich interactive cards (package, locker, PIN)."""
    text: str = Field(..., description="Fallback text summary of the card")
    card_type: str = Field(..., description="Card template identifier (e.g., 'package_pickup')")
    card_data: dict[str, Any] = Field(default_factory=dict, description="Structured card attributes")
    suggested_actions: list[str] = Field(default_factory=list, description="Follow-up quick reply action chips")


class StreamTokenContent(BaseModel):
    """Content payload for live WebSocket token streaming."""
    token: str = Field(..., description="Streaming word or sub-token")
    agent: str | None = Field(None, description="Generating agent name")
    accumulated_text: str | None = Field(None, description="Full accumulated text so far")


class ApprovalGateContent(BaseModel):
    """Content payload for supervisor or security approval gates."""
    text: str = Field(..., description="Explanation of required approval")
    approval_id: str | None = Field(None, description="Pending approval ID")
    action: str | None = Field(None, description="Sensitive action triggered")
    compartment: str | None = Field(None, description="Locker compartment targeted")
    status: Literal["pending", "approved", "rejected"] = Field("pending", description="Current gate status")
    actions: list[str] = Field(default_factory=lambda: ["Approve", "Reject"], description="Available choices")


class SystemEventContent(BaseModel):
    """Content payload for real-time hardware, IoT, or broker push events."""
    event_type: str = Field(..., description="Event name (e.g. 'COMPARTMENT_OPENED')")
    details: dict[str, Any] = Field(default_factory=dict, description="Event metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatMessage(BaseModel):
    """Universal Standard Message Envelope for live streaming, REST APIs, and database persistence."""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}", description="Unique message ID")
    conversation_id: str = Field(..., description="Parent conversation or session identifier")
    type: str = Field("user_message", description="Discriminated message type")
    sender: MessageSender = Field(default_factory=lambda: MessageSender(role="user", name="User"))
    content: dict[str, Any] = Field(default_factory=dict, description="Dynamic payload based on type")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Turn-level metadata")
    user: dict[str, Any] | None = Field(default=None, description="User necessary information object")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="UTC creation timestamp")

    # Backward-compatible fields
    id: str | None = None
    session_id: str | None = None
    role: Literal["user", "assistant", "system"] | None = None
    sender_name: str | None = None
    agent_name: str | None = None
    message_type: str | None = None
    card_payload: dict[str, Any] | None = None
    suggested_actions: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_message_payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. message_id / id
            msg_id = data.get("message_id") or data.get("id") or f"msg_{uuid.uuid4().hex[:12]}"
            data["message_id"] = msg_id
            data["id"] = msg_id

            # 2. conversation_id / session_id
            conv_id = data.get("conversation_id") or data.get("session_id") or ""
            data["conversation_id"] = conv_id
            data["session_id"] = conv_id

            # 3. user info extraction
            user_info = data.get("user") or data.get("user_info")
            if not user_info and isinstance(data.get("metadata"), dict):
                user_info = data["metadata"].get("user") or data["metadata"].get("user_info")
            if not user_info and isinstance(data.get("sender"), dict):
                user_info = data["sender"].get("user") or data["sender"].get("user_info")
            if user_info:
                data["user"] = user_info

            # 4. sender and role
            sender_data = data.get("sender")
            if isinstance(sender_data, dict):
                role = sender_data.get("role", "user")
                name = sender_data.get("name") or ("Assistant" if role == "assistant" else "User")
                sender_id = sender_data.get("id")
            else:
                role = data.get("role") or "user"
                name = data.get("sender_name") or data.get("agent_name") or ("Assistant" if role == "assistant" else "User")
                sender_id = data.get("agent_name")
            data["sender"] = {
                "role": role,
                "name": name,
                "id": sender_id,
                "user": user_info,
                "user_info": user_info,
            }

            data["role"] = role
            data["sender_name"] = name
            if role == "assistant" and not data.get("agent_name"):
                data["agent_name"] = name

            # 5. type / message_type
            raw_msg_type = data.get("message_type")
            raw_type = data.get("type") or raw_msg_type or ("user_message" if role == "user" else "agent_message")
            if raw_type == "text":
                standard_type = "user_message" if role == "user" else "agent_message"
            elif raw_type == "card":
                standard_type = "agent_card"
            else:
                standard_type = raw_type

            data["type"] = standard_type
            data["message_type"] = raw_msg_type or standard_type

            # 5. content: normalize to dynamic dict
            raw_content = data.get("content")
            if isinstance(raw_content, str):
                content_dict = {"text": raw_content}
                if data.get("card_payload"):
                    content_dict["card_data"] = data["card_payload"]
                    content_dict["card_type"] = data["card_payload"].get("card_type", "custom_card")
                if data.get("suggested_actions"):
                    content_dict["suggested_actions"] = data["suggested_actions"]
                if role == "user":
                    content_dict.setdefault("attachments", [])
                data["content"] = content_dict
            elif isinstance(raw_content, dict):
                raw_content.setdefault("text", "")
                if data.get("card_payload") and "card_data" not in raw_content:
                    raw_content["card_data"] = data["card_payload"]
                if data.get("suggested_actions") and "suggested_actions" not in raw_content:
                    raw_content["suggested_actions"] = data["suggested_actions"]
                if role == "user":
                    raw_content.setdefault("attachments", [])

            # Extract card_payload & suggested_actions aliases from content dict
            if isinstance(data.get("content"), dict):
                if not data.get("card_payload"):
                    data["card_payload"] = data["content"].get("card_data")
                if not data.get("suggested_actions"):
                    data["suggested_actions"] = data["content"].get("suggested_actions", [])

        return data

    @property
    def text(self) -> str:
        """Extract primary readable text string."""
        if isinstance(self.content, dict):
            return self.content.get("text", "")
        return str(self.content)


class ChatSession(BaseModel):
    """Session-level conversation envelope managing multi-tenant isolation and history."""
    session_id: str = Field(..., description="Unique conversation session ID")
    conversation_id: str | None = None
    user_id: str = Field(..., description="Verified primary user identifier")
    tenant_id: str = Field(..., description="Tenant identifier for strict data isolation")
    channel: str = Field("webchat", description="Communication channel (e.g., 'webchat', 'teams', 'slack')")
    user: dict[str, Any] | None = Field(default=None, description="User necessary information object")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Session creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last activity timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Session-level metadata (building, unit, location)"
    )
    messages: list[ChatMessage] = Field(
        default_factory=list, description="Ordered conversation history turns"
    )

    @model_validator(mode="before")
    @classmethod
    def sync_conversation_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sid = data.get("session_id") or data.get("conversation_id")
            if sid:
                data["session_id"] = sid
                data["conversation_id"] = sid
            if not data.get("user") and isinstance(data.get("metadata"), dict):
                data["user"] = data["metadata"].get("user")
        return data


class ChatHistoryResponse(BaseModel):
    """Response returned when fetching chat session history."""
    conversation_id: str = Field(..., description="Parent conversation ID")
    session_id: str = Field(..., description="Legacy alias for conversation_id")
    user_id: str
    tenant_id: str
    channel: str
    user: dict[str, Any] | None = Field(default=None, description="User necessary information object")
    total_messages: int
    messages: list[ChatMessage]

    @model_validator(mode="before")
    @classmethod
    def sync_history_ids(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sid = data.get("session_id") or data.get("conversation_id")
            if sid:
                data["session_id"] = sid
                data["conversation_id"] = sid
            if not data.get("user") and isinstance(data.get("metadata"), dict):
                data["user"] = data["metadata"].get("user")
        return data

