from datetime import timedelta, datetime

from rest_framework.settings import APISettings, api_settings
from accounts.app_settings import ObjDict


DEFAULTS = {
    # 'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'SECURE_HASH_ALGORITHM': 'hashlib.sha3_512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=10),
    'LAST_USE_TO_EXPIRY': timedelta(hours=1),
    'TOKEN_LIMIT_PER_USER': 10,
    'AUTO_REFRESH': False,
    'MIN_REFRESH_INTERVAL': 60,
    'AUTH_HEADER_PREFIX': 'Token',
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
    'TOKEN_PREFIX': '',
    'SERIALIZERS':  ObjDict(
        {
            'AUTH_TOKEN': 'accounts.authtoken.serializers.TokenSerialier',
        }
    ),
    'MODELS': ObjDict(
        {
            'AUTH_TOKEN': 'accounts.authtoken.models.AuthToken',
            'AUTH_TOKEN_INFORMATION': 'accounts.authtoken.models.AuthTokenInformation'
        }
    ),
}

IMPORT_STRINGS = {
    'SECURE_HASH_ALGORITHM',
    'AUTH_TOKEN_MODEL',
    'AUTH_TOKEN_INFORMATION_MODEL',
    'AUTH_TOKEN_SEIALIZER',
}

token_settings = APISettings(defaults=DEFAULTS, import_strings=IMPORT_STRINGS)

class CONSTANTS:
    '''
    Constants cannot be changed at runtime
    '''
    TOKEN_KEY_LENGTH = 15
    DIGEST_LENGTH = 128
    MAXIMUM_TOKEN_PREFIX_LENGTH = 10

    def __setattr__(self, *args, **kwargs):
        raise Exception('''
            Constant values must NEVER be changed at runtime, as they are
            integral to the structure of database tables
            ''')


CONSTANTS = CONSTANTS()
