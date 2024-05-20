import random
import string
from datetime import timedelta
from random import randint
from django.db import models
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.app_settings import account_settings
from accounts.validators import (
    UnicodeUsernameValidator,
    NationalCodeValidator,
    HomePhoneNumberValidator,
    PostalCodeValidator,
)
from phonenumber_field import modelfields
from utils.db.mixins.timestamp import TimeStampMixin


def create_username():
    return "".join(
        random.choice(string.ascii_letters + "0123456789") for i in range(15)
    )


class Roles(models.IntegerChoices):
    NOT_DEFINED = 1, "not defined"
    STUDENT = 2, "student"
    TEACHER = 3, "teacher"
    SUPERVISOR = 5, "supervisor"
    ADMIN = 7, "admin"
    TEACHER_SUPERVISOR = TEACHER[0] * SUPERVISOR[0], "teacher and supervisor"
    TEACHER_ADMIN = TEACHER[0] * ADMIN[0], "teacher and admin"


class VerificationStatus(models.IntegerChoices):
    NONE = 1, _("None of them have been verified.")
    PHONE = 2, _("The mobile number is verified.")
    EMAIL = 3, _("Email address is verified.")
    BOTH = 6, _("Both of them are verified.")


class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if username:
            GlobalUserModel = apps.get_model(
                self.model._meta.app_label, self.model._meta.object_name
            )
            username = GlobalUserModel.normalize_username(username)
        else:
            username = create_username()
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if extra_fields.get("role") is None:
            extra_fields.setdefault("role", Roles.NOT_DEFINED)
        if extra_fields.get("role") % Roles.ADMIN.numerator == 0:
            raise ValueError("You are not allowed.")
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Roles.ADMIN)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("role") % Roles.ADMIN != 0:
            raise ValueError("Superuser must have admin role.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(username, email, password, **extra_fields)


class User(TimeStampMixin, AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and _ only."),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    phone_number = modelfields.PhoneNumberField(
        unique=True,
        error_messages={
            "unique": _("A user with that phone number already exists."),
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    role = models.PositiveSmallIntegerField(
        choices=Roles.choices, default=Roles.NOT_DEFINED
    )
    verification_status = models.PositiveSmallIntegerField(
        choices=VerificationStatus.choices, default=VerificationStatus.NONE
    )

    objects = MyUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

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

    @property
    def is_staff(self):
        return self.role % Roles.ADMIN == 0

    def is_student(self):
        return self.role % Roles.STUDENT == 0

    def is_teacher(self):
        return self.role % Roles.TEACHER == 0

    def is_supervisor(self):
        return self.role % Roles.SUPERVISOR == 0

    def set_rule(self, role):
        if self.role % role != 0:
            self.role *= role
        self.save()

    def __str__(self):
        return f"{self.username}"

    class Meta:
        db_table = "user"


class UserExtra(TimeStampMixin):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE, related_name="user_info"
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

    class Meta:
        db_table = "user_extra"


class VerificationCodeMixin(models.Model):
    code = models.CharField(
        unique=True,
        max_length=6,
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("When was this token generated")
    )
    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default="",
        blank=True,
    )
    resended = models.PositiveSmallIntegerField(
        default=0,
    )

    def code_remaining_time(self):
        remainingـtime = (
            self.created_at
            + account_settings.EMAIL_CONFIRMATION_AND_PASSWORD_RESSET_TOKEN_EXPIRE_MINUTES
        ) - timezone.now()
        return remainingـtime if remainingـtime > timedelta() else None

    def __str__(self):
        return f"{self.user} | {self.code}"

    @classmethod
    def generate_verification_code(cls):
        """generate code where does not exist in this table (try at last 5 times)"""
        code = 0
        count = 1
        while True:
            code = randint(100000, 999999)
            if cls.objects.filter(code=code).count() == 0 or count > 5:
                break
            count += 1
        return code

    class Meta:
        abstract = True


class EmailVerificationCode(VerificationCodeMixin):
    class Meta:
        db_table = "accounts_email_verification_code"


class PasswordResetCode(VerificationCodeMixin):
    class Meta:
        db_table = "accounts_password_reset_code"


def delete_expired_codes(CodeClass):
    """
    it will delete all expired codes and return last deleted code
    if there is no expired code it will return 0
    """
    code = 0
    for codei in CodeClass.objects.filter().iterator():
        if codei.code_remaining_time() is None:
            code = codei.code
            codei.delete()
    return code
