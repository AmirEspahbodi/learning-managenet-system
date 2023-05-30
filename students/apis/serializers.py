from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from accounts.validators import validate_password, name_validator
from students.models import Student
UserModel = get_user_model()

class StudentRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    school = serializers.CharField()
    degree = serializers.IntegerField()
    field = serializers.CharField()
    
    class Meta:
        model = UserModel
        fields =    ('first_name', 'last_name', 'email', 'username', 'phone_number', 
                    'password1', 'password2', 'school', 'degree', 'field')

    def validate(self, data, *args, **kwargs):
        if data['password1'] != data['password2']:
            raise exceptions.ValidationError(
                {'password': "The two password fields didn't match."}
            )
        
        # use default django password validator (user information similarity) too
        first_name_error = name_validator(data['first_name'], return_error=True)
        last_name_error = name_validator(data['last_name'], return_error=True)
        name_errors = {}
        name_errors.update({'first_name':first_name_error} if first_name_error else {})
        name_errors.update({'last_name':last_name_error} if last_name_error else {})
        if name_errors:
            raise serializers.ValidationError(
                name_errors
            )
        return data
    
    def create(self, validated_data):
        user = UserModel(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        student = Student.objects.create(
            user=user,
            school=validated_data['school'],
            degree=validated_data['degree'],
            field=validated_data['field'],
        )
        return student
