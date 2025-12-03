import asyncio


class EventLock:
    def __init__(self):
        self._event = asyncio.Event()
        self._event.set()

    async def wait(self):
        await self._event.wait()

    def turn_on(self):
        """Включаем блокировку: новые acquire будут ждать"""
        self._event.clear()

    def turn_off(self):
        """Выключаем блокировку: все проходят сразу"""
        self._event.set()

    def reset(self):
        self._event = asyncio.Event()
        self._event.set()
