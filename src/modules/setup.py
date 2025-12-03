from pyrogram.types import InlineKeyboardMarkup

from .modules import Runway
from src.core.syntx import SyntxBot


async def setup_modules(bot: SyntxBot):
    await press_button(bot, Runway.cancel_button)


async def press_button(bot, button_text):
    async for message in bot.client.get_chat_history(bot.id, limit=200):
        markup = message.reply_markup
        if isinstance(markup, InlineKeyboardMarkup):
            for row in markup.inline_keyboard:
                for button in row:
                    if button.text == button_text:
                        await message.click(button.text)