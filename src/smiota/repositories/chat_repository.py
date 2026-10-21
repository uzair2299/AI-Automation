"""Chat Session Repository: Abstract storage contract and In-Memory implementation.

Provides decoupled chat session and conversation history persistence.
Enables transparent swapping between In-Memory, Redis, and PostgreSQL backends
via configuration with zero modifications to API endpoints or agent orchestration.
"""
from abc import ABC, abstractmethod
import asyncio
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
import uuid

from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.schemas.chat_session import ChatMessage, ChatSession, MessageType


class BaseChatRepository(ABC):
    """Abstract Repository interface defining chat session and message storage operations."""

    @abstractmethod
    async def get_or_create_session(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        channel: str = "webchat",
        metadata: dict[str, Any] | None = None,
    ) -> ChatSession:
        """Retrieve an existing session or initialize a new one with user/tenant bindings."""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> ChatSession | None:
        """Fetch a session by its unique session_id."""
        pass

    @abstractmethod
    async def append_message(
        self,
        session_id: str,
        role: Literal["user", "assistant", "system"],
        content: str | dict[str, Any],
        sender_name: str | None = None,
        agent_name: str | None = None,
        message_type: MessageType = "user_message",
        card_payload: dict[str, Any] | None = None,
        suggested_actions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        message_id: str | None = None,
    ) -> ChatMessage:
        """Append a message turn to the session history."""
        pass

    @abstractmethod
    async def get_messages(self, session_id: str, limit: int = 50) -> list[ChatMessage]:
        """Fetch ordered recent message turns for a given session."""
        pass

    @abstractmethod
    async def list_user_sessions(self, user_id: str, tenant_id: str | None = None) -> list[ChatSession]:
        """List active sessions belonging to a specific user (scoped by tenant)."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        pass

    @abstractmethod
    async def clear_all(self) -> None:
        """Clear all stored sessions (primarily for testing and cache reset)."""
        pass


class InMemoryChatRepository(BaseChatRepository):
    """Thread-safe In-Memory Chat Session Repository with TTL eviction and sliding window.

    - Thread Safety: Guarded by asyncio.Lock.
    - Sliding Window: Keeps the last `max_turns * 2` messages per session.
    - TTL / LRU Eviction: Automatically removes sessions inactive longer than `ttl_hours`.
    """

    def __init__(self, ttl_hours: int = 24, max_turns: int = 20):
        self.ttl = timedelta(hours=ttl_hours)
        self.max_turns = max_turns
        self._sessions: OrderedDict[str, ChatSession] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        channel: str = "webchat",
        metadata: dict[str, Any] | None = None,
    ) -> ChatSession:
        async with self._lock:
            self._evict_expired()
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.updated_at = datetime.now(UTC)
                if metadata:
                    session.metadata.update(metadata)
                self._sessions.move_to_end(session_id)
                return session

            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                tenant_id=tenant_id,
                channel=channel,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                metadata=metadata or {},
                messages=[],
            )
            self._sessions[session_id] = session
            return session

    async def get_session(self, session_id: str) -> ChatSession | None:
        async with self._lock:
            self._evict_expired()
            return self._sessions.get(session_id)

    async def append_message(
        self,
        session_id: str,
        role: Literal["user", "assistant", "system"],
        content: str | dict[str, Any],
        sender_name: str | None = None,
        agent_name: str | None = None,
        message_type: MessageType = "user_message",
        card_payload: dict[str, Any] | None = None,
        suggested_actions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        message_id: str | None = None,
    ) -> ChatMessage:
        async with self._lock:
            self._evict_expired()

            # Auto-provision fallback session if message arrives without prior explicit initialization
            if session_id not in self._sessions:
                self._sessions[session_id] = ChatSession(
                    session_id=session_id,
                    user_id="anonymous",
                    tenant_id="default",
                    channel="webchat",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    metadata={},
                    messages=[],
                )

            session = self._sessions[session_id]

            # Normalize dynamic content dict
            if isinstance(content, str):
                content_dict: dict[str, Any] = {"text": content}
                if role == "user":
                    content_dict["attachments"] = attachments or []
                if card_payload:
                    content_dict["card_data"] = card_payload
                    content_dict["card_type"] = card_payload.get("card_type", "custom_card")
                if suggested_actions:
                    content_dict["suggested_actions"] = suggested_actions
            else:
                content_dict = dict(content)
                content_dict.setdefault("text", "")
                if role == "user":
                    content_dict.setdefault("attachments", attachments or [])
                if card_payload and "card_data" not in content_dict:
                    content_dict["card_data"] = card_payload
                    content_dict["card_type"] = card_payload.get("card_type", "custom_card")
                if suggested_actions and "suggested_actions" not in content_dict:
                    content_dict["suggested_actions"] = suggested_actions

            # Map legacy display types to standard types
            effective_type = message_type
            if effective_type in ("text", "user_message", "agent_message"):
                effective_type = "user_message" if role == "user" else "agent_message"
            elif effective_type in ("card", "agent_card"):
                effective_type = "agent_card"

            sender_display = sender_name or agent_name or ("Assistant" if role == "assistant" else "User")
            msg = ChatMessage(
                message_id=message_id or f"msg_{uuid.uuid4().hex[:12]}",
                conversation_id=session_id,
                type=effective_type,
                sender={
                    "role": role,
                    "name": sender_display,
                    "id": agent_name if role == "assistant" else None,
                },
                content=content_dict,
                metadata=metadata or {},
                created_at=datetime.now(UTC),
                # Legacy fields for backward compatibility
                id=message_id or f"msg_{uuid.uuid4().hex[:12]}",
                session_id=session_id,
                role=role,
                sender_name=sender_display,
                agent_name=agent_name,
                message_type=message_type,
                card_payload=card_payload,
                suggested_actions=suggested_actions or [],
            )

            session.messages.append(msg)

            # Apply sliding window: retain up to max_turns * 2 (1 user + 1 assistant turn)
            max_messages = self.max_turns * 2
            if len(session.messages) > max_messages:
                session.messages = session.messages[-max_messages:]

            session.updated_at = datetime.now(UTC)
            self._sessions.move_to_end(session_id)
            return msg

    async def get_messages(self, session_id: str, limit: int = 50) -> list[ChatMessage]:
        async with self._lock:
            self._evict_expired()
            session = self._sessions.get(session_id)
            if not session:
                return []
            return session.messages[-limit:]

    async def list_user_sessions(self, user_id: str, tenant_id: str | None = None) -> list[ChatSession]:
        async with self._lock:
            self._evict_expired()
            matching: list[ChatSession] = []
            for session in reversed(self._sessions.values()):
                if session.user_id == user_id:
                    if tenant_id is None or session.tenant_id == tenant_id:
                        matching.append(session)
            return matching

    async def delete_session(self, session_id: str) -> bool:
        async with self._lock:
            return self._sessions.pop(session_id, None) is not None

    async def clear_all(self) -> None:
        async with self._lock:
            self._sessions.clear()

    def _evict_expired(self) -> None:
        """Internal helper to drop sessions inactive beyond the configured TTL."""
        now = datetime.now(UTC)
        expired_keys = [
            sid for sid, sess in self._sessions.items()
            if now - sess.updated_at > self.ttl
        ]
        for sid in expired_keys:
            del self._sessions[sid]


# Singleton in-memory store initialized with settings
_settings = get_settings()
_in_memory_instance = InMemoryChatRepository(
    ttl_hours=getattr(_settings, "CHAT_SESSION_TTL_HOURS", 24),
    max_turns=getattr(_settings, "CHAT_SESSION_MAX_TURNS", 20),
)


def get_chat_repository() -> BaseChatRepository:
    """Factory provider returning the configured Chat Repository.

    To switch to PostgreSQL, Redis, or Mongo in the future:
    Simply add the corresponding class here and return it based on CHAT_STORAGE_BACKEND.
    FastAPI endpoints and the Multi-Agent Orchestrator remain 100% unchanged.
    """
    settings = get_settings()
    backend = getattr(settings, "CHAT_STORAGE_BACKEND", "memory").lower()

    if backend == "redis":
        # Future Redis Repository integration
        logger.debug("Redis Chat Repository selected (falling back to memory until redis adapter configured)")
        return _in_memory_instance
    elif backend == "postgres":
        # Future PostgreSQL Repository integration
        logger.debug("PostgreSQL Chat Repository selected (falling back to memory until postgres adapter configured)")
        return _in_memory_instance

    return _in_memory_instance
