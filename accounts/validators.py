import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.app_settings import account_settings



@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r"^[\w]+\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and _ characters."
    )
    flags = 0

def checkNationalCode(value):
    if len(value) != 10 or value in [
        '0000000000', '1111111111', '2222222222',
        '3333333333','4444444444', '5555555555',
        '6666666666', '7777777777','8888888888', '9999999999'
    ]:
            return False
    sum = 0
    if value[-1].isdigit():
        control_num = int(value[-1])
    else:
        return False
    for i in range(0, len(value)-1):
        if (value[i].isdigit()):
            sum+= (10-i) * int(value[i])
        else:
            return False
    rem = sum % 11
    if rem<2:
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
    if not (re.match('[0-9]{7,}', value[3:]) and re.match('^0[^0,9][^2,9]$', value[0:3])):
        raise ValueError("شماره تلفن وارد شده معتبر نیست")

def PostalCodeValidator(value):
    if not re.match('[1-9]{10}', value):
        raise ValueError('کد ملی معتبر نیست')


def validate_password(password):
    password
    if len(password) < account_settings.PASSWORD_MIN_LENGTH:
        return[ "Password must be a minimum of {0} characters.".format(account_settings.PASSWORD_MIN_LENGTH)]
    has_upper = False
    has_lower = False
    has_number = False
    has_other = False
    for p in password:
        if p.isdecimal():
            has_number=True
        elif p.islower():
            has_lower=True
        elif p.isupper():
            has_upper=True
        else:
            has_other=True
    password_errors = []
    if not has_upper:
        password_errors.append("Password must contain uppercase letters")
    if not has_lower:
        password_errors.append("Password must contain lowercase letters")
    if not has_number:
        password_errors.append("Password must contain numbers")
    if not has_other:
        password_errors.append("Password must contain at least one other character")
    return password_errors

def validate_6_digit_code(value):
    int_value = int(value)
    if not (int_value < 999999 and int_value > 100000):
        raise ValueError("code must be in range 100000-999999")