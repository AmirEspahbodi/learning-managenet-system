from django.db import models
from django.contrib.auth import get_user_model
from core.db.mixins.timestamp import TimeStampMixin

# Create your models here.

User = get_user_model()


class Teacher(TimeStampMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="teacher_user",
        db_index=True,
    )
    experience = models.PositiveSmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.user

    def __str__(self):
        return (
            "teacher " + str(self.user.first_name) + " " + str(str(self.user.last_name))
        )


class Published(TimeStampMixin):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
    )
    published = models.CharField(max_length=300)
    publisher = models.CharField(max_length=300)

    def __str__(self):
        return str(self.published[:50] + self.publisher[:50])

    class Meta:
        db_table = "teacher_published"


class Education(TimeStampMixin):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    education = models.CharField(max_length=300)
    university = models.CharField(max_length=300)

    def __str__(self):
        return str(self.education[:50] + self.university[:50])

    class Meta:
        db_table = "teacher_education"
