import html

from pyrogram import filters
from pyrogram.types import Message


def always_true():
    async def func(flt, _, message: Message):
        return True
    return filters.create(func)

def startswith(text: str):
    async def func(flt, _, message: Message):
        if message.text:
            return html.unescape(message.text).startswith(flt.text)
        elif message.caption:
            return html.unescape(message.caption).startswith(flt.text)
    return (filters.text | filters.caption) & filters.create(func, text=text.strip())

def endswith(text: str):
    async def func(flt, _, message: Message):
        if message.text:
            return html.unescape(message.text).endswith(flt.text)
        elif message.caption:
            return html.unescape(message.caption).endswith(flt.text)
    return (filters.text | filters.caption) & filters.create(func, text=text.strip())

def button_map_filter(expected_map):
    """Создает фильтр для сообщений с кнопками, совпадающими с expected_map"""
    async def func(_, __, message: Message):
        if not message.reply_markup or not getattr(message.reply_markup, "inline_keyboard", None):
            return False
        actual_map = []
        for row in message.reply_markup.inline_keyboard:
            # Собираем текст всех кнопок в ряду
            actual_map.append([button.text for button in row])
        return actual_map == expected_map
    return filters.create(func)

def contains(text: str):
    async def func(flt, _, message: Message):
        if message.text:
            return flt.text in html.unescape(message.text)
        elif message.caption:
            return flt.text in html.unescape(message.caption)
    return (filters.text | filters.caption) & filters.create(func, text=text.strip())

def message_exists(ext_message: Message):
    async def func(flt, _, message: Message):
        return not ext_message.empty
    return filters.create(func, ext_message=ext_message)

def equals(text: str):
    async def func(flt, _, message: Message):
        if message.text:
            return html.unescape(message.text) == flt.text
        elif message.caption:
            return html.unescape(message.caption) == flt.text
    return (filters.text | filters.caption) & filters.create(func, text=text.strip())

def is_replying_to(target_message: Message):
    async def func(flt, _, message: Message):
        return message.reply_to_message_id == flt.target_message.id
    return filters.reply & filters.create(func, target_message=target_message)

def has_inline_button(button_text: str):
    async def func(flt, _, message: Message):
        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if button.text == flt.button_text:
                    return True
        return False
    return filters.inline_keyboard & filters.create(func, button_text=button_text)

def message_id_in(messages: list[Message]):
    async def func(flt, _, message: Message):
        ids = [i.id for i in flt.messages]
        return message.id in ids
    return filters.create(func, messages=messages)