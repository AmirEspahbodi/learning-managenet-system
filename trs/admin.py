from django.contrib import admin

from .models import Room, TimeSlot, Semester
# Register your models here.


class RoomTimeSlots(admin.TabularInline):
    model = TimeSlot
    
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    ordering = ('room_title',)
    list_display = ('room_number', 'room_title', 'capacity')
    list_filter = ('room_title', 'capacity')
    inlines = [RoomTimeSlots]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    ordering = ('day', 'start')
    fieldsets = (
        (None, {'fields': (('room_number', 'day'),)}),
        ('time', {'fields':(("start", "end"),)})
    )
    list_display = ('id', "room_number", "day", "start", "end", 'display' )
    list_filter = ("room_number", "day", "start", "end")

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    ordering = ('semester_id',)
    fieldsets = (
        (None, {'fields': ('year', 'semester')}),
    )
    list_display = ('semester_id', 'year', 'semester')