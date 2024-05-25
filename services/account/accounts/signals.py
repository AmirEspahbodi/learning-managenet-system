from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import UserExtra


User = get_user_model()


@receiver(post_save, sender=User)
def craete_user_information(sender, instance, created, **kwargs):
    if created:
        pass
        # TIP
        # create associated student or teacher
