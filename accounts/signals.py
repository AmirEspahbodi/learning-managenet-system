from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import UserInformation

User = get_user_model()

@receiver(post_save, sender=User)
def send_email_verification(sender, instance, created, **kwargs):
    if created:
        UserInformation.objects.create(user=instance)
