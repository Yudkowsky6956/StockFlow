class WrongAPIException(Exception):
    """If Pyrogram refuses API_ID or API_HASH"""

class WrongPhoneException(Exception):
    """If Pyrogram refuses given phone number"""