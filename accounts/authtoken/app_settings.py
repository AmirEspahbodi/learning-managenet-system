from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings, api_settings
from accounts.app_settings import ObjDict


USER_SETTINGS = getattr(settings, 'REST_KNOX', None)

DEFAULTS = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=10),
    'LAST_USE_TO_EXPIRY': timedelta(minutes=20),
    'SERIALIZER': ObjDict(
        {
            'USER_SERIALIZER': None
        }
    ),
    'TOKEN_LIMIT_PER_USER': 10,
    'AUTO_REFRESH': False,
    'MIN_REFRESH_INTERVAL': 60,
    'AUTH_HEADER_PREFIX': 'Token',
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
    'TOKEN_MODEL': 'accounts.authtoken.AuthToken',
    'TOKEN_PREFIX': '',
}

IMPORT_STRINGS = {
    'SECURE_HASH_ALGORITHM',
    'TOKEN_MODEL',
}

token_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    global knox_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'REST_KNOX':
        knox_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)
        if len(knox_settings.TOKEN_PREFIX) > CONSTANTS.MAXIMUM_TOKEN_PREFIX_LENGTH:
            raise ValueError("Illegal TOKEN_PREFIX length")


setting_changed.connect(reload_api_settings)


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
