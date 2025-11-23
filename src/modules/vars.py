from src.core.vars import CONFIG_FOLDER

MODULES_YML = CONFIG_FOLDER / "modules.yml"

YOUR_REQUEST = "📍 Ваш запрос: {}"
TARIFF = "Тариф:"
MENU_MESSAGE = "/menu"
MENU_RESPONSE = "🏠 Главное меню \nВыберите нужный раздел 👇"

VIDEO_NAME = "VIDEO"
VIDEO_MESSAGE = "/video"
VIDEO_RESPONSE = "🎬 Видео будущего\nВыберите раздел для работы с видео 👇"
VIDEO_IMAGE_RESPONSE = "✅ {} изображение добавлено."
VIDEO_IMAGE_RESPONSE_ONE = "✅ Изображение добавлено."
VIDEO_URL_BUTTON = "🎞️ Настроить и запустить"

GPT_NAME = "GPT"
GPT_MESSAGE = "/gpt"
GPT_RESPONSE = "💡 GPTs/Claude/Gemini\n\n🎙️ Голосом, ✍️ текстом, 🌅 изображением — задавайте любые вопросы удобным способом и SYNTX тут же найдёт решение + 🌐 выход в интернет (только 4 версия модели)."
GPT_VIEW_FULL_DIALOG = "💬 Просмотреть весь диалог"

DESIGN_NAME = "DESIGN"
DESIGN_MESSAGE = "/design"
DESIGN_RESPONSE = "🎨 Дизайн с ИИ\nВыберите раздел для работы с изображением 👇"

DESIGN_QUALITY_LINK = "на качественную версию."

DESIGN_SELECT_1 = "Выбрать #1"
DESIGN_SELECT_2 = "Выбрать #2"
DESIGN_SELECT_3 = "Выбрать #3"
DESIGN_SELECT_4 = "Выбрать #4"
DESIGN_SUB_1 = "V1 Sub"
DESIGN_SUB_2 = "V2 Sub"
DESIGN_SUB_3 = "V3 Sub"
DESIGN_SUB_4 = "V4 Sub"
DESIGN_STR_1 = "V1 Str"
DESIGN_STR_2 = "V2 Str"
DESIGN_STR_3 = "V3 Str"
DESIGN_STR_4 = "V4 Str"
DESIGN_DOWNLOAD_ALL = "💾 Скачать всё"
DESIGN_SEED = "🌱 Seed"
DESIGN_REPEAT = "↻ Повторить"
DESIGN_REQUEST = "📄 Запрос"
DESIGN_REMIX_THIN = "✏️  Remix: тонкий"
DESIGN_REMIX_CREATIVE = "✏️  Remix: креативный"
DESIGN_REMIX_THIN_SMALL = "✏️ Remix: тонкий"
DESIGN_REMIX_CREATIVE_SMALL = "✏️ Remix: креативный"
DESIGN_LEFT = "⬅️"
DESIGN_RIGHT = "➡️"
DESIGN_UP = "⬆️"
DESIGN_DOWN = "⬇️"
DESIGN_UPSCALE_THIN = "↗️ Масштаб x2 (тонкий)"
DESIGN_UPSCALE_CREATIVE = "↘️ Масштаб x2 (креативный)"
DESIGN_EXPAND_2X = "🔍Расширить 2x"
DESIGN_EXPAND_1_5X = "🔍Расширить 1.5x"
DESIGN_EDITOR = "✂️ Редактор"
DESIGN_RETEXTURE = "🧵 Ретекстура"
DESIGN_REMIX = "♻️ Remix"

NANO_ORIGINAL_BUTTON_MAP = [[DESIGN_REMIX]]

MIDJOURNEY_DESIGN_ORIGINAL_BUTTON_MAP = [
    [DESIGN_SELECT_1, DESIGN_SELECT_2],
    [DESIGN_SELECT_3, DESIGN_SELECT_4],
    [DESIGN_SUB_1, DESIGN_SUB_2, DESIGN_SUB_3, DESIGN_SUB_4],
    [DESIGN_STR_1, DESIGN_STR_2, DESIGN_STR_3, DESIGN_STR_4],
    [DESIGN_DOWNLOAD_ALL, DESIGN_SEED],
    [DESIGN_REPEAT, DESIGN_REQUEST]
]

MIDJOURNEY_DESIGN_SELECTED_BUTTON_MAP = [
    [DESIGN_EXPAND_2X, DESIGN_EXPAND_1_5X],
    [DESIGN_REMIX_THIN_SMALL],
    [DESIGN_REMIX_CREATIVE_SMALL],
    [DESIGN_LEFT, DESIGN_RIGHT, DESIGN_UP, DESIGN_DOWN],
    [DESIGN_UPSCALE_THIN],
    [DESIGN_UPSCALE_CREATIVE],
    [DESIGN_EDITOR],
    [DESIGN_RETEXTURE]
]

MIDJOURNEY_DESIGN_UPSCALED_BUTTON_MAP = [
    [DESIGN_REMIX_THIN],
    [DESIGN_REMIX_CREATIVE],
    [DESIGN_EXPAND_2X, DESIGN_EXPAND_1_5X],
    [DESIGN_EDITOR]
]

AUDIO_NAME = "AUDIO"
AUDIO_MESSAGE = "/audio"
AUDIO_RESPONSE = "🔊 Аудио с ИИ\nВыберите раздел для работы с аудио 👇"

EMPTY_PROMPT = "Без запроса"

VEO_MESSAGE = "⭕ Veo"
VEO_RESPONSE = "⭕ Veo\n\nПередовая модель искусственного интеллекта от Google. Позволяет генерировать видео в качестве 720p и до 8 секунд."
VEO_MODEL_END = "🧮 Модель: #veo"

SORA_MESSAGE = "🌙 SORA"
SORA_RESPONSE = "🌙 SORA\n\nПередовая модель искусственного интеллекта, способная преобразовывать текстовые описания или картинки и видео в динамичные видеоролики с разрешением до 1080p и продолжительностью до 10 секунд."
SORA_MODEL_END = "🧮 Модель: #Sora"

RUNWAY_MESSAGE = "🎞️ RunWay: Gen-4"
RUNWAY_RESPONSE = "🎞️ RunWay: Gen-4\n\nОтправьте ✍️ текстовое задание на удобном языке или 🌄 загрузите до 3 изображений, чтобы сгенерировать видео в топовой нейросети Runway👇"
RUNWAY_MODEL_END = "🧮 Модель: #RunWay"
RUNWAY_CANCEL_BUTTON = "❌ Отменить операцию"

MINIMAX_MESSAGE = "🎦 Hailuo MiniMax"
MINIMAX_RESPONSE = "🎦 Hailuo MiniMax\n\n[BETA] Оживляйте изображения или отправляйте текстовое задание на удобном языке чтобы создать видео в популярной нейросети Hailuo MINIMAX 👇"

LUMA_MESSAGE = "📽️ Luma: DM"
LUMA_RESPONSE = "📽️ Luma: DM\n\nОживляйте изображения, загружайте начальный и конечный кадр или отправляйте текстовое задание на удобном языке чтобы создать видео от 5 до 30 секунд в Luma: Dream Machine 👇"

MIDJOURNEY_MESSAGE = "🌄 MidJourney"
MIDJOURNEY_RESPONSE = "🌄 MidJourney\n\n✍️ Напишите текстом, что хотите нарисовать или 🌄 загрузите изображение для обработки 👇"

NANO_MESSAGE = "🍌 Nano Banana"
NANO_RESPONSE = "🍌 Nano Banana\n\nНашумевшая нейросеть от Google: Gemini Flash 2.5 Banana. Прекрасно понимает контекст и ювелирно меняет объекты на ваших картинках, сохраняя исходное качество."

