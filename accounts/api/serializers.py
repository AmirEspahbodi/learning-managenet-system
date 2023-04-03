from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.validators import validate_password, validate_6_digit_code

User = get_user_model()

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
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number', 'role', 'password1', 'password2')

    def validate(self, data, *args, **kwargs):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                "The two password fields didn't match."
            )
        return data    
    
    def create(self, validated_data):
        user = User(
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