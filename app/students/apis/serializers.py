from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import serializers
from students.models import Student, FinancialAids
from accounts.apis.serializers import UserRegisterL1Serializer, UserSerializerBaseInfo

User = get_user_model()


class StudentRegisterSerializer(serializers.ModelSerializer):
    user = UserRegisterL1Serializer(
        many=False
    )

    class Meta:
        model = Student
        fields = ('school', 'degree', 'field', 'user')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number'],
        )
        student = Student.objects.create(user=user, **validated_data)
        return student


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializerBaseInfo()

    class Meta:
        model = Student
        fields = ('user', 'school', 'degree', 'field')


class StudentFinancialAidsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinancialAids
        fields = ("applying_reason", "annual_income", "ability_to_pay")

    def save(self, student, course, **kwargs):
        validated_data = {**self.validated_data, **kwargs, "student":student,"course":course}
        self.instance = self.create(validated_data)
        return self.instance



class ShowFinancialAids(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = FinancialAids
        fields = ('id', 'student', 'applying_reason', 'annual_income', 'ability_to_pay',
                  'result', 'created_at', 'is_accepted', 'reviewed')



class StudentFinancialAids(serializers.ModelSerializer):
    class Meta:
        model = FinancialAids
        fields = ('id', 'applying_reason', 'annual_income', 'ability_to_pay',
                  'result', 'created_at', 'is_accepted', 'reviewed')