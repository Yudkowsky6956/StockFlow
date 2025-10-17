import asyncio
from src.core.syntx.video import VideoInBot
from .vars import *


class Veo(VideoInBot):
    agent_message = VEO_MESSAGE
    agent_response = VEO_RESPONSE
    semaphore: asyncio.Semaphore = asyncio.Semaphore(VEO_BATCH_SIZE)