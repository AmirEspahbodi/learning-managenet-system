from django.utils import timezone

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.authtoken import crypto
from accounts.authtoken.app_settings import CONSTANTS, token_settings

sha = token_settings.SECURE_HASH_ALGORITHM

User = settings.AUTH_USER_MODEL


class AuthTokenManager(models.Manager):
    def create(
        self,
        user,
        prefix=token_settings.TOKEN_PREFIX
    ):
        token = prefix + crypto.create_token_string()
        digest = crypto.hash_token(token)
        instance = super(AuthTokenManager, self).create(
            token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH],
            digest=digest,
            user=user)
        
        return instance, token

def expiry_set():
    return timezone.now() + token_settings.TOKEN_TTL

class AuthToken(models.Model):

    objects = AuthTokenManager()

    digest = models.CharField(
        max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    
    token_key = models.CharField(
        max_length=CONSTANTS.TOKEN_KEY_LENGTH,
        db_index=True)
    
    user = models.ForeignKey(User, null=False, blank=False,
                             related_name='auth_token_set', on_delete=models.CASCADE)
    
    last_use = models.DateTimeField(auto_now=True)
    
    expiry = models.DateTimeField(default=expiry_set)

    def __str__(self):
        return '%s : %s' % (self.digest, self.user)
    class Meta:
        db_table = "authtoken_auth_token"

class AuthTokenInformation(models.Model):
    authToken = models.OneToOneField(
        AuthToken,
        primary_key=True,
        on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default="",
        blank=True,
    )
    class Meta:
        db_table = "authtoken_auth_token_information"