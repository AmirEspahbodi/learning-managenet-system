from rest_framework import serializers
from ..models import Exam

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = (
            'id', 'session', 'title',
            'description', 'exam_number',
            'start_datetime', 'end_datetime'
        )
    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        return response