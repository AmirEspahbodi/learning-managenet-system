from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import exceptions, serializers
from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from accounts.validators import validate_password, validate_6_digit_code, UnicodeUsernameValidator


UserModel = get_user_model()

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailConfirmationCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)


class PasswordResetValidateCodeSerializer(serializers.Serializer):
    code = serializers.CharField(validators=[validate_6_digit_code])


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)
    password1 = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(required=True)
    def validate(self, data, *args, **kwargs):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                "The two password fields didn't match."
            )
        
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number', 'role', 'password1', 'password2')

    def validate(self, data, *args, **kwargs):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                "The two password fields didn't match."
            )
        return data    
    
    def create(self, validated_data):
        user = UserModel(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    login_field = serializers.CharField(
        label=_("login_field"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def get_auth_user(self, username, email, phone_number, password):
        if not ((username or email or phone_number) and password):
            msg = _('not valid login information.')
            raise exceptions.ValidationError(msg)
        user = authenticate(self.context.get('request'), username=username, email=email, phone_number=phone_number, password=password)
        return user

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_email_verification_status(user):
        if (not user.is_email_verified()):
            raise serializers.ValidationError(_('E-mail is not verified.'))

    @staticmethod
    def validate_phone_number_verification_status(user):
        if (not user.is_phone_number_verified()):
            raise serializers.ValidationError(_('phone number is not verified.'))
    
    @staticmethod
    def validate_email_or_phone_number_verification_status(user):
        if not (user.is_phone_number_verified() or user.is_email_verified()):
            raise serializers.ValidationError(_('either phone number or email address must be verifiy.'))

    def validate(self, attrs):
        login_field = attrs.get('login_field')
        password = attrs.get('password')
        email, username, phone_number = None, None, None

        try:
            validate_email(login_field)
            email = login_field
        except ValidationError:
            pass

        if not email:
            try:
                UnicodeUsernameValidator()(login_field)
                username = login_field
            except ValidationError:
                pass

        if not (email or phone_number):
            try:
                validate_international_phonenumber(login_field)
                phone_number = login_field
            except ValidationError:
                pass
        
        user = self.get_auth_user(username, email, phone_number, password)

        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        self.validate_auth_user_status(user)

        if email:
            self.validate_email_verification_status(user)

        if phone_number:
            self.validate_phone_number_verification_status(user)

        if username:
            self.validate_email_or_phone_number_verification_status(user)

        attrs['user'] = user
        return attrs
