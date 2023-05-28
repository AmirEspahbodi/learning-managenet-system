from django.db import models

from django.contrib.auth import get_user_model
from courses.models import Course, CourseTimes
# Create your models here.

CustomUser = get_user_model()
class Student(models.Model):
    user = models.OneToOneField(
        CustomUser,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='student_user',
        db_index=True
    )
    school = models.CharField(max_length=300, blank=True)
    degree = models.PositiveSmallIntegerField(default=0 , blank=True)
    field = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"student: {self.user.username} ({self.user.last_name})"


class StudentTakes(models.Model):
    id = models.BigAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_takes'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    
    is_student_access = models.BooleanField(default=False)
    is_student_paid_percentage = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.student} {self.course}'

    class Meta:
            constraints = [
            models.UniqueConstraint(
                fields=[
                    'student',
                    'course'
                ],
                name='unique_student_course'
            )
        ]
