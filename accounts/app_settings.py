from datetime import timedelta

from django.utils.module_loading import import_string
from rest_framework.settings import APISettings

class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ObjDict, self).__getattribute__(item)

        return val

DEFAULTS = {
    'PASSWORD_MIN_LENGTH': 10,
    'EMAIL_CONFIRMARION_AND_PASSWORD_RESSET_TOKEN_EXPIRE_MINUTES': timedelta(minutes=5),
    'LAST_LOGIN_TO_GET_NEW_TOKEN_MINUTES': timedelta(minutes=2),
    'SERIALIZERS': ObjDict(
        {
            'EMAIL': 'accounts.api.serializers.EmailSerializer',
            'EMAIL_VERIFICATION_CODE': 'accounts.api.serializers.EmailConfirmationCodeSerializer',
            'PASSWORD_RESET_CONFIRM': 'accounts.api.serializers.PasswordResetConfirmSerializer',
            'PASWORD_RESET_VERIFY_CODE': 'accounts.api.serializers.PasswordResetValidateCodeSerializer',
            'USER_REGISTER': 'accounts.api.serializers.UserRegisterSerializer',
            'USER_LOGIN': 'accounts.api.serializers.UserLoginSerializer'
        }
    ),
    'MODELS': ObjDict(
        {
            'PASSWORD_RESET_CODE': 'accounts.models.PasswordResetCode',
            'EMAIL_VERIFICATION_CODE': 'accounts.models.EmailConfirmationCode',
            'VERIFICATION_STATUS': 'accounts.models.VERIFICATION_STATUS'
        }
    )
}

account_settings = APISettings(defaults=DEFAULTS)
