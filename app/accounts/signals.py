from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import UserInformation
from students.models import Student
from teachers.models import Teacher

User = get_user_model()


@receiver(post_save, sender=User)
def craete_user_information(sender, instance, created, **kwargs):
    if created:
        UserInformation.objects.create(user=instance)
        if instance.is_student() and not Student.objects.filter(user=instance).exists():
            Student.objects.create(user=instance)

        if instance.is_teacher() and not Teacher.objects.filter(user=instance).exists():
            Teacher.objects.create(user=instance)
