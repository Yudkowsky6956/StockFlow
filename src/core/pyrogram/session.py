import asyncio
from functools import wraps
from pathlib import Path

from loguru import logger
from pyrogram import Client
from pyrogram.errors.exceptions import ApiIdInvalid, PhoneNumberBanned, PhoneNumberInvalid

from src.core.global_config import get_global_config
from src.utils.normalize import normalize_phone
from .exceptions import WrongAPIException, WrongPhoneException
from .secrets import get_api_hash, get_api_id
from .vars import SESSION_FOLDER


def handle_client_exceptions(exc):
    """Handles and categorizes exceptions"""
    if isinstance(exc, ApiIdInvalid):
        logger.error("Pyrogram was provided with incorrect API_ID or API_HASH")
        raise WrongAPIException
    elif isinstance(exc, AttributeError) and "The API key is required for new authorizations." in str(exc):
        logger.error("Pyrogram was provided with incorrect API_ID or API_HASH")
        raise WrongAPIException
    elif isinstance(exc, (PhoneNumberInvalid, PhoneNumberBanned)):
        logger.error("Pyrogram was provided with incorrect phone number")
        raise WrongPhoneException
    else:
        raise

def client_error_handler(function):
    """Decorator that handles exceptions in sync and async methods"""
    if asyncio.iscoroutinefunction(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except Exception as e:
                handle_client_exceptions(e)
        return wrapper
    else:
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                handle_client_exceptions(e)
        return wrapper

class Session:
    """Class that represents one Pyrogram session"""
    session_folder = SESSION_FOLDER

    def __init__(self, phone_number: str = None):
        self._client = None

        if not phone_number:
            phone_number = self.current()
        self.phone_number = normalize_phone(phone_number)

    @client_error_handler
    def _get_client(self):
        """Initializes and returns Pyrogram Client"""
        logger.debug(f"Initializing Pyrogram client ({self.phone_number})")
        return Client(
            name=self.phone_number,
            phone_number=self.phone_number,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=self.session_folder
        )

    @client_error_handler
    def connect(self) -> Client:
        """Starts and returns client"""
        self.client.start()
        me = self.client.get_me()
        logger.success(f"👤 Authorized as {me.first_name} (@{me.username})")
        return self.client

    @client_error_handler
    async def connect_async(self) -> Client:
        """Async starts and returns client"""
        await self.client.start()
        me = await self.client.get_me()
        logger.success(f"👤 Authorized as {me.first_name} (@{me.username})")
        return self.client

    def stop(self):
        """Stops client if connected"""
        if self.is_connected():
            self.client.stop()
            logger.info(f"Stopping client ({self.phone_number})")

    async def stop_async(self):
        """Async stops client if connected"""
        if self.is_connected():
            await self.client.stop()
            logger.info(f"Stopping client ({self.phone_number})")

    def is_connected(self):
        return self.client and self.client.is_connected

    @property
    def client(self) -> Client:
        if not self._client:
            self._client = self._get_client()
        return self._client

    @property
    def api_id(self) -> int:
        return get_api_id()

    @property
    def api_hash(self) -> str:
        return get_api_hash()

    @property
    def path(self) -> Path:
        return self.session_folder / f"{self.phone_number}.session"

    def remove(self):
        """Removes session file from session folder"""
        if self.path.exists():
            logger.debug(f"Session with name \"{self.path.name}\" was removed")
            self.path.unlink()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    async def __aenter__(self):
        return await self.connect_async()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_async()

    @classmethod
    def all(cls):
        """Returns all session names in session folder"""
        cls.ensure_paths()
        return [file.stem for file in cls.session_folder.glob("*.session")]

    @classmethod
    def current(cls):
        return get_global_config().get("telegram_account")

    @classmethod
    def ensure_paths(cls):
        """Ensures that session folder exists"""
        cls.session_folder.mkdir(parents=True, exist_ok=True)



