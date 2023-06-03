from rest_framework import serializers
from ..models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('id', 'session', 'description', 'assignment_number', 'start_datetime', 'end_datetime')