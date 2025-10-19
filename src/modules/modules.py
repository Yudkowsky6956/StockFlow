import asyncio
from src.core.syntx.video import VideoInBot, VideoMiniApp
from .vars import *


class Veo(VideoInBot):
    syntx_name = VEO_NAME
    agent_message = VEO_MESSAGE
    agent_response = VEO_RESPONSE
    semaphore: asyncio.Semaphore = asyncio.Semaphore(VEO_BATCH_SIZE)
    max_photos_per_batch = VEO_MAX_PHOTOS_PER_BATCH

class Sora(VideoInBot):
    syntx_name = SORA_NAME
    agent_message = SORA_MESSAGE
    agent_response = SORA_RESPONSE
    semaphore: asyncio.Semaphore = asyncio.Semaphore(SORA_BATCH_SIZE)
    max_photos_per_batch = SORA_MAX_PHOTOS_PER_BATCH

class Runway(VideoMiniApp):
    syntx_name = RUNWAY_NAME
    agent_message = RUNWAY_MESSAGE
    agent_response = RUNWAY_RESPONSE
    semaphore: asyncio.Semaphore = asyncio.Semaphore(RUNWAY_BATCH_SIZE)
    max_photos_per_batch = RUNWAY_MAX_PHOTOS_PER_BATCH