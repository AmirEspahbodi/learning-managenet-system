from django.db import models


class Semseters(models.IntegerChoices):
    FIRST_SEMESTER = 1, 'First semester'
    SECOND_SEMESTER = 2, 'Second semester'
    THIRD_SEMESTER = 3, 'Third semester'


class Days_Of_Week(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
    SUNDAY = 7, 'Sunday'


# Create your models here.
class Semester(models.Model):
    semester_id = models.PositiveIntegerField(primary_key=True)
    year = models.CharField(
        max_length=10,
        help_text="Enter the year as follows: 1400-1401"
        # validators=[]
    )
    semester = models.PositiveSmallIntegerField(choices=Semseters.choices)
    def __str__(self):
        return str(self.semester_id)

    def __unicode__(self):
        return self.semester_id


class Room(models.Model):
    room_number = models.SmallAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
    )
    room_title = models.CharField(max_length=300, unique=True)
    capacity = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return f"{self.room_title}"


class TimeSlot(models.Model):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
    )
    room_number = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )
    day = models.PositiveSmallIntegerField(choices=Days_Of_Week.choices)
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room_number', 'day', 'start'],
                name='unique_trs_time_slot'
            )
        ]
        db_table = "trs_time_slot"
        db_table_comment = "The time period depends on the day of the week and the room."

    def __str__(self):
        return f"{self.room_number} {Days_Of_Week.labels[self.day-1]} {self.start} {self.end}"

    def display(self): 
        return f"{self.room_number} {Days_Of_Week.labels[self.day-1]} {self.start} {self.end}"
