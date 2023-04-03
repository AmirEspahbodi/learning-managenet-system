from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import setUp_user_email_confirmation
from .models import UserInformation

User = get_user_model()

@receiver(post_save, sender=User)
def send_email_verification(sender, instance, created, **kwargs):
    if created:
        UserInformation.objects.create(user=instance)
        try:
            setUp_user_email_confirmation(user=instance)
        except BaseException as e:
            print(f"email setup faild for {instance.username}\nhere is the exception: {e} | {e.args}")
