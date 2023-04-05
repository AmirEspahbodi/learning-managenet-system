from datetime import timedelta
from rest_framework.settings import APISettings

DEFAULTS = {
    'PASSWORD_MIN_LENGTH': 10,
    'EMAIL_CONFIRMARION_AND_PASSWORD_RESSET_TOKEN_EXPIRE_MINUTES': timedelta(minutes=5),
    'LAST_LOGIN_TO_GET_NEW_TOKEN_MINUTES': timedelta(minutes=2),
}
IMPORT_STRINGS = set()
account_settings = APISettings(defaults=DEFAULTS, import_strings=IMPORT_STRINGS)
