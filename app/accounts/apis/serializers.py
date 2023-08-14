from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError as djangoValidationError
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from accounts.validators import (
    validate_password,
    validate_6_digit_code,
    UnicodeUsernameValidator,
    name_validator,
)
from accounts.validators import (
    NationalCodeValidator,
    PostalCodeValidator,
    HomePhoneNumberValidator
)
from accounts.app_settings import account_settings
from accounts.models import UserInformation, PasswordResetCode

UserModel = get_user_model()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailConfirmationCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)


class PasswordResetVerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(validators=[validate_6_digit_code])


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)
    new_password1 = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    set_password_form_class = SetPasswordForm

    def validate(self, attrs):
        try:
            resetCode = PasswordResetCode.objects.get(code=attrs["code"])
        except ObjectDoesNotExist:
            raise ValidationError("wrong code")
        self.set_password_form = self.set_password_form_class(
            user=resetCode.user,
            data=attrs,
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        attrs["verificationCode"] = resetCode
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(
        max_length=128, validators=[validate_password]
    )
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm
    set_password_form = None

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = account_settings.OLD_PASSWORD_FIELD_ENABLED
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop("old_password")

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = _(
                "Your old password was entered incorrectly. Please enter it again."
            )
            raise serializers.ValidationError(err_msg)
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user,
            data=attrs,
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs


class UserRegisterL1Serializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserModel
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "phone_number",
            "role",
            "password1",
            "password2",
        )

    def validate(self, data, *args, **kwargs):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "The two password fields didn't match."}
            )

        # use default django password validator (user information similarity) too
        first_name_error = name_validator(data["first_name"], return_error=True)
        last_name_error = name_validator(data["last_name"], return_error=True)
        if first_name_error or last_name_error:
            raise serializers.ValidationError(
                {
                    **({"first_name": first_name_error} if first_name_error else {}),
                    **({"last_name": last_name_error} if last_name_error else {}),
                }
            )
        return data

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password1"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            username=validated_data.get("username"),
            role=validated_data.get("role"),
        )
        return user


class UserRegisterL2Serializer(serializers.ModelSerializer):
    national_code = serializers.CharField(validators=[NationalCodeValidator])
    postal_code = serializers.CharField(validators=[PostalCodeValidator])
    home_phone_number = serializers.CharField(validators=[HomePhoneNumberValidator])
            
    class Meta:
        model = UserInformation
        fields = (
            "user",
            "national_code",
            "secondary_phone_number",
            "province",
            "city",
            "address",
            "postal_code",
            "date_of_birth",
            "father_name",
            "home_phone_number",
        )

    def validate(self, data, *args, **kwargs):
        father_name_error = name_validator(data.get("father_name"), return_error=True)
        if father_name_error:
            raise serializers.ValidationError(father_name_error)
        return data

    def create(self, validated_data):
        userInformation = UserInformation.objects.create(
            user_id=validated_data.get("user_id"),
            national_code=validated_data.get("national_code"),
            secondary_phone_number=validated_data.get("secondary_phone_number"),
            province=validated_data.get("province"),
            city=validated_data.get("city"),
            address=validated_data.get("address"),
            postal_code=validated_data.get("postal_code"),
            date_of_birth=validated_data.get("date_of_birth"),
            father_name=validated_data.get("father_name"),
            home_phone_number=validated_data.get("home_phone_number"),
        )
        
        return userInformation


class UserLoginSerializer(serializers.Serializer):
    login_field = serializers.CharField(label=_("login_field"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def get_auth_user(self, username, email, phone_number, password):
        if not ((username or email or phone_number) and password):
            msg = {"login_field": "not valid login information."}
            raise exceptions.ValidationError(msg)
        user = authenticate(
            self.context.get("request"),
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
        )
        return user

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = {"non_field_errors": "User account is disabled."}
            raise exceptions.ValidationError(msg)

    def validate(self, attrs):
        login_field = attrs.get("login_field")
        password = attrs.get("password")
        email, username, phone_number = None, None, None
        try:
            validate_email(login_field)
            email = login_field
        except djangoValidationError:
            pass

        if not email:
            try:
                UnicodeUsernameValidator()(login_field)
                username = login_field
            except djangoValidationError:
                pass

        if not (email or phone_number):
            try:
                validate_international_phonenumber(login_field)
                phone_number = login_field
            except djangoValidationError:
                pass
        user = self.get_auth_user(username, email, phone_number, password)

        if not user:
            try:
                if username:
                    user = UserModel.objects.get(username=username)
                elif email:
                    user = UserModel.objects.get(email=email)
                elif phone_number:
                    user = UserModel.objects.get(phone_number=phone_number)
            except UserModel.DoesNotExist:
                pass

            msg = {
                "non_field_errors": "Unable to log in with provided credentials."
                if user
                else "no user found with with provided credentials"
            }
            raise exceptions.ValidationError(msg)

        self.validate_auth_user_status(user)

        attrs["user"] = user
        return attrs


class MobileGlobalSettingsSerializer(serializers.Serializer):
    logout_on_exit = serializers.BooleanField()
    auth_token_last_use_to_expire = serializers.JSONField()


class UserSerializerTeacherSearch(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("first_name", "last_name")


class UserSerializerNames(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "first_name", "last_name")

class UserSerializerBaseInfo(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "first_name", "last_name", "username", "email", "phone_number")