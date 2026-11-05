"""Multi-turn conversation memory and sliding window context manager."""
from typing import Optional
from smiota.core.cache import get_cache_service
from smiota.core.logging import logger


class ConversationMemory:
    """Manages short-term conversation context across chat channels."""

    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.max_turns = max_turns
        self._in_memory_store: list[dict[str, str]] = []

    async def add_message(self, role: str, content: str) -> None:
        """Append message to conversation history with window pruning."""
        msg = {"role": role, "content": content}
        self._in_memory_store.append(msg)
        if len(self._in_memory_store) > self.max_turns * 2:
            self._in_memory_store = self._in_memory_store[-self.max_turns * 2:]

        cache = await get_cache_service()
        key = f"memory:session:{self.session_id}"
        await cache.set(key, self._in_memory_store, ttl_seconds=86400)

    async def get_messages(self) -> list[dict[str, str]]:
        """Retrieve recent conversation turns."""
        cache = await get_cache_service()
        key = f"memory:session:{self.session_id}"
        cached = await cache.get(key)
        if cached and isinstance(cached, list):
            self._in_memory_store = cached
        return self._in_memory_store

    async def clear(self) -> None:
        """Clear memory for current session."""
        self._in_memory_store = []
        cache = await get_cache_service()
        await cache.delete(f"memory:session:{self.session_id}")
