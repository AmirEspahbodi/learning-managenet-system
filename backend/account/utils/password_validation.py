import collections
import gzip
import re
from difflib import SequenceMatcher
from pathlib import Path
from django.utils.functional import cached_property, lazy
from django.utils.translation import ngettext


def validate_password(password, first_name, last_name, email, phone_number):

    error = []
    MinimumLengthValidator().validate(password, error)
    UserAttributeSimilarityValidator().validate(
        password,
        error,
        collections.namedtuple(
            "User", ["first_name", "last_name", "email", "phone_number"]
        )(first_name, last_name, email, phone_number),
    )
    CommonPasswordValidator().validate(password, error)
    HasUpperLowerNumericOtherPasswordValidator.validate(password, error)
    return error


def exceeds_maximum_length_ratio(password, max_similarity, value):
    """
    Test that value is within a reasonable range of password.

    The following ratio calculations are based on testing SequenceMatcher like
    this:

    for i in range(0,6):
      print(10**i, SequenceMatcher(a='A', b='A'*(10**i)).quick_ratio())

    which yields:

    1 1.0
    10 0.18181818181818182
    100 0.019801980198019802
    1000 0.001998001998001998
    10000 0.00019998000199980003
    100000 1.999980000199998e-05

    This means a length_ratio of 10 should never yield a similarity higher than
    0.2, for 100 this is down to 0.02 and for 1000 it is 0.002. This can be
    calculated via 2 / length_ratio. As a result we avoid the potentially
    expensive sequence matching.
    """
    pwd_len = len(password)
    length_bound_similarity = max_similarity / 2 * pwd_len
    value_len = len(value)
    return pwd_len >= 10 * value_len and value_len < length_bound_similarity


class MinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, error: list):
        if len(password) < self.min_length:
            error.append(
                f"This password is too short. It must contain at least {self.min_length}character."
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_length)d character.",
            "Your password must contain at least %(min_length)d characters.",
            self.min_length,
        ) % {"min_length": self.min_length}


class UserAttributeSimilarityValidator:
    DEFAULT_USER_ATTRIBUTES = ("username", "first_name", "last_name", "email")

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        if max_similarity < 0.1:
            raise ValueError("max_similarity must be at least 0.1")
        self.max_similarity = max_similarity

    def validate(self, password, error: list, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    error.append(
                        "Your password can’t be too similar to your other personal information."
                    )


class CommonPasswordValidator:
    @cached_property
    def DEFAULT_PASSWORD_LIST_PATH(self):
        return Path(__file__).resolve().parent / "common-passwords.txt.gz"

    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        if password_list_path is CommonPasswordValidator.DEFAULT_PASSWORD_LIST_PATH:
            password_list_path = self.DEFAULT_PASSWORD_LIST_PATH
        try:
            with gzip.open(password_list_path, "rt", encoding="utf-8") as f:
                self.passwords = {x.strip() for x in f}
        except OSError:
            with open(password_list_path) as f:
                self.passwords = {x.strip() for x in f}

    def validate(self, password, error: list):
        if password.lower().strip() in self.passwords:
            error.append("Your password can’t be a commonly used password.")


class HasUpperLowerNumericOtherPasswordValidator:
    @staticmethod
    def validate(password, error: list):
        has_upper = False
        has_lower = False
        has_number = False
        has_other = False
        for p in password:
            if p.isdecimal():
                has_number = True
            elif p.islower():
                has_lower = True
            elif p.isupper():
                has_upper = True
            else:
                has_other = True
        msg = "Password must contain "
        if not has_upper and not has_lower:
            msg = "uppercase and lowercase letters "
        elif not has_upper:
            msg += "uppercase letters "
        elif not has_lower:
            msg += "lowercase letters "
        if not has_upper or not has_lower:
            msg += "and "
        if not has_number:
            msg += "numbers"
        if not has_upper or not has_lower or not has_number:
            msg += "and "
        if not has_other:
            msg += "least one other character"
        error.append(msg)
