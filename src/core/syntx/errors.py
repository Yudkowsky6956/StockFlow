from dataclasses import dataclass


@dataclass
class HandlerError:
    message: str
    delay: int = 0
    log: str = None
    reply: bool = True
    fatal: bool = False
    mark: bool = False
    lock: bool = False


BLOCK_1 = HandlerError(
    message="Ваше сообщение содержит недопустимое содержание и нейросеть его не пропустит.",
    log="error.handlers.block",
    mark=True
)
BLOCK_2 = HandlerError(
    message="Пожалуйста, попробуйте перефразировать запрос.",
    log="error.handlers.block",
    mark=True
)
BLOCK_3 = HandlerError(
    message="❌ Недопустимый запрос",
    log="error.handlers.block",
    mark=True
)
BLOCK_4 = HandlerError(
    message="❌ Произошла ошибка. Пожалуйста, попробуйте еще раз или обратитесь в службу поддержки @syntxhelp.",
    log="error.handlers.block",
    mark=True
)
BLOCK_5 = HandlerError(
    message="Операция была отменена модератором сервиса.",
    log="error.handlers.block",
    mark=True,
    reply=True
)
TOO_SHORT = HandlerError(
    message="Ошибка: too short",
    log="error.handlers.too_short",
    mark=True
)
BLOCK_FULL = HandlerError(
    message="Пожалуйста, ознакомьтесь с правилами и инструкциями, как правильно отправлять запросы.",
    delay=20*60,
    log="error.handlers.block_full",
    lock=True
)
YOU_ALREADY_LOAD_IMAGE = HandlerError(
    message="⚠️ Вы уже загрузили изображение, пожалуйста удалите его и/или отправьте текстовой запрос для старта генерации 👇",
    delay=20,
    log="error.handlers.you_already_load_image",
)
WAIT_UNTIL_NEXT_REQUEST = HandlerError(
    message="Запросы отправляются слишком быстро.",
    delay=5,
    log="error.handlers.wait_until_next_request",
    lock=True
)
MODEL_ERROR_1 = HandlerError(
    message="Временные неполадки в работе нейросети. Пожалуйста, попробуйте немного позже.",
    delay=5*60,
    log="error.handlers.model_not_working",
    lock=True
)
MODEL_ERROR_2 = HandlerError(
    message="Модель в данный момент, к сожалению, недоступна.",
    delay=5*60,
    log="error.handlers.model_not_working",
    reply=False,
    lock=True
)
REQUEST_LIMIT = HandlerError(
    message="Достигнут лимит одновременных запросов.",
    delay=5*60,
    log="error.handlers.request_limit",
    reply=False,
    lock=True
)
NO_TOOL = HandlerError(
    message="⚠️ Не выбран инструмент для работы с чат-ботом.",
    delay=20,
    log="error.handlers.no_tool",
    reply=False
)
PLEASE_WAIT = HandlerError(
    message="⚠️ Пожалуйста, подождите",
    delay=5,
    log="error.handlers.please_wait",
    lock=True
)
ON_UPDATE = HandlerError(
    message="на обновлении. Пожалуйста, попробуйте еще раз немного позже.",
    log="error.handlers.on_update",
    delay=60 * 10,
    reply=False,
    lock=True
)



AFTER_REQUEST_ERROR = [
    REQUEST_LIMIT, NO_TOOL, WAIT_UNTIL_NEXT_REQUEST
]


ALL_ERRORS = [
    BLOCK_1, BLOCK_2, BLOCK_3, BLOCK_4, BLOCK_5, TOO_SHORT,
    BLOCK_FULL, MODEL_ERROR_1, YOU_ALREADY_LOAD_IMAGE,
    WAIT_UNTIL_NEXT_REQUEST, MODEL_ERROR_2, REQUEST_LIMIT, NO_TOOL,
    PLEASE_WAIT, ON_UPDATE,
]
