from rest_framework.serializers import ModelSerializer
from ..models import TimeSlot, Semester, Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ('room_number', 'room_title')


class TimeSlotSerializer(ModelSerializer):
    room_number = RoomSerializer()

    class Meta:
        model = TimeSlot
        fields = ('room_number', 'day', 'start', 'end')


class SemesterSerializer(ModelSerializer):
    class Meta:
        model = Semester
        fields = ('year', 'semester')
