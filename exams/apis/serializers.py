from rest_framework import serializers
from ..models import Exam

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('id', 'session', 'description', 'exam_number', 'start_datetime', 'end_datetime')