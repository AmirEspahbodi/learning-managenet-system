from rest_framework import serializers
from rest_framework.fields import BooleanField, IntegerField, CharField
from accounts.apis.serializers import UserSerializerTeacherSearch
from ..models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializerTeacherSearch()

    class Meta:
        model = Teacher
        fields = ("user", "experience")


class StudentAccessSerializer(serializers.Serializer):
    student_id = IntegerField()
    access = BooleanField()


class FinancialAidsResultSerializer(serializers.Serializer):
    financial_id = IntegerField()
    user_id = IntegerField()
    result = CharField()
    is_accepted = BooleanField()
