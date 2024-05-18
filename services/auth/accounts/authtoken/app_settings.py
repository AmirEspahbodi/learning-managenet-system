from datetime import timedelta
from hashlib import sha3_256
from rest_framework.settings import api_settings


class TokenSettings:
    SECURE_HASH_ALGORITHM: sha3_256 = sha3_256
    AUTH_TOKEN_CHARACTER_LENGTH: int = 64
    TOKEN_TTL: timedelta = timedelta(days=10)
    LAST_USE_TO_EXPIRY: timedelta = timedelta(days=10)
    TOKEN_LIMIT_PER_USER: int = 10
    AUTO_REFRESH: bool = False
    MIN_REFRESH_INTERVAL: int = 60
    AUTH_HEADER_PREFIX: str = "Token"
    TOKEN_PREFIX: str = ""
    EXPIRY_DATETIME_FORMAT: str = api_settings.DATETIME_FORMAT


token_settings = TokenSettings()


class CONSTANTS:
    TOKEN_KEY_LENGTH = 15
    DIGEST_LENGTH = 128
    MAXIMUM_TOKEN_PREFIX_LENGTH = 10

    def __setattr__(self, *args, **kwargs):
        raise Exception(
            """
            Constant values must NEVER be changed at runtime, as they are
            integral to the structure of database tables
            """
        )


CONSTANTS = CONSTANTS()
