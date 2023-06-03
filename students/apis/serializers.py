from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from accounts.validators import validate_password, name_validator
from students.models import Student
from accounts.apis.serializers import UserRegisterSerializer

User = get_user_model()

class StudentRegisterSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer(
        many=False
    )
    class Meta:
        model = Student
        fields = ('school', 'degree', 'field', 'user')
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=       user_data['username'],
            email=          user_data['email'],
            password=       user_data['password1'],
            first_name=     user_data['first_name'],
            last_name=      user_data['last_name'],
            phone_number=   user_data['phone_number'],
        )
        student = Student.objects.create(user=user,**validated_data)
        return student
