from rest_framework.serializers import ModelSerializer
from accounts.apis.serializers import UserSerializerTeacherSearch
from ..models import Teacher


class TeacherSerializer(ModelSerializer):
    user = UserSerializerTeacherSearch()

    class Meta:
        model = Teacher
        fields = ('user', 'experience')
