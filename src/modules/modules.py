from src.modules.gpt import GPTModule
from src.modules.video import VideoInBot, VideoMiniApp
from src.modules.design import NanoModule, MidjourneyModule
from .vars import *


class Veo(VideoInBot):
    agent_message = VEO_MESSAGE
    agent_response = VEO_RESPONSE

class Sora(VideoInBot):
    agent_message = SORA_MESSAGE
    agent_response = SORA_RESPONSE

class Runway(VideoMiniApp):
    agent_message = RUNWAY_MESSAGE
    agent_response = RUNWAY_RESPONSE
    cancel_button = RUNWAY_CANCEL_BUTTON

class MiniMax(VideoInBot):
    agent_message = MINIMAX_MESSAGE
    agent_response = MINIMAX_RESPONSE

class Luma(VideoInBot):
    agent_message = LUMA_MESSAGE
    agent_response = LUMA_RESPONSE

class GPT(GPTModule):
    pass

class Midjourney(MidjourneyModule):
    CONFIG_PARAMETERS = MidjourneyModule.CONFIG_PARAMETERS + ["flags"]
    agent_message = MIDJOURNEY_MESSAGE
    agent_response = MIDJOURNEY_RESPONSE
    output_amount = 4

class Nano(NanoModule):
    agent_message = NANO_MESSAGE
    agent_response = NANO_RESPONSE
