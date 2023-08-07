from datetime import timedelta

from django.utils.module_loading import import_string


class ImportableDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(
                    v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ImportableDict, self).__getattribute__(item)

        return val


class AcountSettings:
    LOGOUT_ON_PASSWORD_CHANGE = False
    OLD_PASSWORD_FIELD_ENABLED = True
    PASSWORD_MIN_LENGTH = 10
    VERIFICATION_CODE_RESEND_LIMIT = 5
    USERNAME_LENFGTH = 10
    EMAIL_CONFIRMARION_AND_PASSWORD_RESSET_TOKEN_EXPIRE_MINUTES = timedelta(
        minutes=5)


account_settings = AcountSettings
