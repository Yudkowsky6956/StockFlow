import asyncio
from src.core.syntx.video import VideoInBot
from .vars import *


class Veo(VideoInBot):
    agent_message = VEO_MESSAGE
    agent_response = VEO_RESPONSE
    semaphore: asyncio.Semaphore = asyncio.Semaphore(VEO_BATCH_SIZE)

class Sora(VideoInBot):
    agent_message = SORA_MESSAGE
    agent_response = SORA_RESPONSE
    semaphore = asyncio.Semaphore = asyncio.Semaphore(SORA_BATCH_SIZE)