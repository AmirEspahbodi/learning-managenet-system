from rest_framework.serializers import ModelSerializer, Serializer
from accounts.apis.serializers import UserSerializerTeacherSearch
from rest_framework.fields import BooleanField, IntegerField
from ..models import Teacher


class TeacherSerializer(ModelSerializer):
    user = UserSerializerTeacherSearch()

    class Meta:
        model = Teacher
        fields = ('user', 'experience')


class StudentAccessSerializer(Serializer):
    student_id = IntegerField()
    access = BooleanField()
