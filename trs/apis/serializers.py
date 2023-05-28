from rest_framework.serializers import ModelSerializer
from .models import TimeSlot, Semester


class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ('room_number', 'day', 'start', 'end')
        
class SemesterSerializer(ModelSerializer):
    class Meta:
        model = Semester
        fields = ('year', 'semester')