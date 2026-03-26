from pprint import pprint

from src.core.syntx import SyntxBot
from .core_script import FilesScripts


class PrintLastMessage(FilesScripts):
    @classmethod
    async def _run(cls):
        bot = SyntxBot()
        async with bot.client as client:
            history = client.get_chat_history(bot.id, limit=1)
            message = await anext(history)
            pprint(vars(message))