from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Teacher
from accounts.models import Roles

@receiver(post_save, sender = Teacher)
def set_is_teacher_for_teacher_user(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        if not user.is_teacher():
            user.role *= Roles.TEACHER
            user.save()
