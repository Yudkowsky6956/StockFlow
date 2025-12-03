import asyncio
from typing import Any, Optional


class SyntxCurrentModule:
    """
    Asynchronous storage for the current module with a lock for safe access to SyntxAI.
    Ensure if you want to change SyntxAI Module
    """
    _value: Optional[Any] = None
    _lock: Optional[asyncio.Lock] = None

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        return cls._lock

    @classmethod
    async def get(cls) -> Optional[Any]:
        async with cls._get_lock():
            return cls._value

    @classmethod
    async def set(cls, value: Any) -> None:
        async with cls._get_lock():
            cls._value = value

    @classmethod
    async def clear(cls) -> None:
        async with cls._get_lock():
            cls._value = None

    @classmethod
    def reset(cls) -> None:
        cls._value: Optional[Any] = None
        cls._lock: Optional[asyncio.Lock] = None
