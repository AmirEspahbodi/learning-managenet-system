from .models import AuthToken


def delete_expired_tokens():
    AuthToken.objects.filter()


def delete_user_tokens(user):
    AuthToken.objects.filter(user=user)
