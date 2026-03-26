from src.core.syntx.event_lock import EventLock
import asyncio


locks = {
    "syntx_lock": asyncio.Lock(),
    "event_lock": EventLock()
}