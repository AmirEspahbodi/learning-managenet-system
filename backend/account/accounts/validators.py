import re
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from accounts.app_settings import account_settings


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z][\w]+\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and _ characters."
    )
    flags = 0


def checkNationalCode(value):
    if len(value) != 10 or value in [
        "0000000000",
        "1111111111",
        "2222222222",
        "3333333333",
        "4444444444",
        "5555555555",
        "6666666666",
        "7777777777",
        "8888888888",
        "9999999999",
    ]:
        return False
    sum = 0
    if value[-1].isdigit():
        control_num = int(value[-1])
    else:
        return False
    for i in range(0, len(value) - 1):
        if value[i].isdigit():
            sum += (10 - i) * int(value[i])
        else:
            return False
    rem = sum % 11
    if rem < 2:
        if control_num == rem:
            pass
        else:
            return False
    else:
        if rem == 11 - control_num:
            pass
        else:
            return False
    return True


def NationalCodeValidator(value):
    if not checkNationalCode(value):
        raise ValueError("national code is not valid")


def HomePhoneNumberValidator(value):
    if not (
        re.match("[0-9]{7,}", value[3:]) and re.match("^0[^0,9][^2,9]$", value[0:3])
    ):
        raise ValueError("phone number is not valid")


def PostalCodeValidator(value):
    if not re.match("[1-9]{10}", value):
        raise ValueError("postal code is not valid")


def validate_6_digit_code(value):
    int_value = int(value)
    if not (int_value < 999999 and int_value > 100000):
        raise ValidationError("code must be in range 100000-999999")


def name_validator(value, return_error=False):
    if not re.match("^[a-zA-Z ]+$", value):
        if return_error:
            return "valid name must only contains latters"
        else:
            raise ValidationError("valid name contains only latters")
