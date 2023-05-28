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
    'LOGOUT_ON_PASSWORD_CHANGE': False, # False will send new token (all token will be deleted)
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'PASSWORD_MIN_LENGTH': 10,
    'VERIFICATION_CODE_RESEND_LIMIT': 5,
    'EMAIL_CONFIRMARION_AND_PASSWORD_RESSET_TOKEN_EXPIRE_MINUTES': timedelta(minutes=5),
    'SERIALIZERS': ObjDict(
        {
            'EMAIL': 'accounts.apis.serializers.EmailSerializer',
            'EMAIL_VERIFICATION_CODE': 'accounts.apis.serializers.EmailConfirmationCodeSerializer',
            'PASSWORD_RESET_CONFIRM': 'accounts.apis.serializers.PasswordResetConfirmSerializer',
            'PASWORD_RESET_VERIFY_CODE': 'accounts.apis.serializers.PasswordResetVerifyCodeSerializer',
            'USER_REGISTER': 'accounts.apis.serializers.UserRegisterSerializer',
            'USER_LOGIN': 'accounts.apis.serializers.UserLoginSerializer',
            'PASSWORD_CHANGE': 'accounts.apis.serializers.PasswordChangeSerializer',
            'Mobile_Global_Settings':'accounts.apis.serializers.MobileGlobalSettingsSerializer'
        }
    ),
    'MODELS': ObjDict(
        {
            'PASSWORD_RESET_CODE': 'accounts.models.PasswordResetCode',
            'EMAIL_VERIFICATION_CODE': 'accounts.models.EmailVerificationCode',
            'VERIFICATION_STATUS': 'accounts.models.VERIFICATION_STATUS'
        }
    )
}


account_settings = APISettings(defaults=DEFAULTS)
