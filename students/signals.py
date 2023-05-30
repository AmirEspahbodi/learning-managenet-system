from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from accounts.models import Roles

@receiver(post_save, sender = Student)
def set_is_teacher_for_teacher_user(sender, instance, created, **kwargs):
    if created:
        instance.user.set_rule(Roles.STUDENT)
