import random
import string
import unicodedata
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.crypto import salted_hmac
from utils import TimeStampMixin
from accounts.validators import (
    UnicodeUsernameValidator,
    NationalCodeValidator,
    HomePhoneNumberValidator,
    PostalCodeValidator,
)
from phonenumber_field import modelfields
from utils.hasher import check_password, is_password_usable, make_password


def create_username():
    return "".join(
        random.choice(string.ascii_letters + "0123456789") for i in range(15)
    )


class VerificationStatus(models.IntegerChoices):
    NONE = 1, _("None of them have been verified.")
    PHONE = 2, _("The mobile number is verified.")
    EMAIL = 3, _("Email address is verified.")
    BOTH = 6, _("Both of them are verified.")


class User(TimeStampMixin):
    password = models.CharField(_("password"), max_length=128)
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    email = models.EmailField(
        _("email address"),
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and _ only."),
        validators=[UnicodeUsernameValidator()],
    )
    phone_number = modelfields.PhoneNumberField()
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    verification_status = models.PositiveSmallIntegerField(
        choices=VerificationStatus.choices, default=VerificationStatus.NONE
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number"]

    def clean(self):
        setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""

    def is_email_verified(self):
        return self.verification_status % VerificationStatus.EMAIL == 0

    def is_phone_number_verified(self):
        return self.verification_status % VerificationStatus.PHONE == 0

    def __str__(self):
        return self.get_username()

    def get_username(self):
        """Return the username for this User."""
        return getattr(self, self.USERNAME_FIELD)

    def natural_key(self):
        return (self.get_username(),)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @staticmethod
    def set_password(raw_password):
        return make_password(raw_password)

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field.
        """
        return self._get_session_auth_hash()

    def get_session_auth_fallback_hash(self):
        for fallback_secret in settings.SECRET_KEY_FALLBACKS:
            yield self._get_session_auth_hash(secret=fallback_secret)

    def _get_session_auth_hash(self, secret=None):
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(
            key_salt,
            self.password,
            secret=secret,
            algorithm="sha256",
        ).hexdigest()

    @classmethod
    def get_email_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return "email"

    @classmethod
    def normalize_username(cls, username):
        return (
            unicodedata.normalize("NFKC", username)
            if isinstance(username, str)
            else username
        )

    class Meta:
        db_table = "user"


class UserExtra(TimeStampMixin):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE, related_name="user_extra"
    )
    national_code = models.CharField(
        max_length=10, validators=[NationalCodeValidator], blank=True, null=True
    )
    secondary_phone_number = modelfields.PhoneNumberField(blank=True, null=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    province = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    postal_code = models.CharField(
        blank=True, null=True, max_length=20, validators=[PostalCodeValidator]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    home_phone_number = models.CharField(
        max_length=11, validators=[HomePhoneNumberValidator], blank=True, null=True
    )
    ip_address = models.TextField(
        _("The IP address of user when registered"),
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.TextField(
        _("HTTP User Agent"),
        default="",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "user_extra"
