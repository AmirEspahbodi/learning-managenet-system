from datetime import datetime

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import DateTimeField
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from accounts.authtoken.auth import TokenAuthentication
from accounts.authtoken.models import AuthToken, AuthTokenInformation
from accounts.authtoken.settings import knox_settings
from accounts.utils import get_ip_and_user_agent

class LoginView(APIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated,)

    def get_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_token_ttl(self):
        return knox_settings.TOKEN_TTL

    def get_token_prefix(self):
        return knox_settings.TOKEN_PREFIX

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def get_user_serializer_class(self):
        return knox_settings.USER_SERIALIZER

    def get_expiry_datetime_format(self):
        return knox_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def create_token(self):
        instance, token = AuthToken.objects.create(
            user=self.user,
            prefix=self.get_token_prefix()
        )
        (client_ip, is_routable, user_agent_data) = get_ip_and_user_agent(self.request)
        AuthTokenInformation.objects.create(
            authToken = instance,
            ip_address = client_ip if client_ip else is_routable,
            user_agent = user_agent_data,
        )
        user_logged_in.send(sender=self.user.__class__,
                    request=self.request, user=self.user)
        return instance, token

    def get_post_response_data(self, request, token, instance):
        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'not_use_expire_minuts': int(knox_settings.LAST_USE_TO_EXPIRY.seconds/60),
            'token_key': token
        }
        return data

    def check_exceeding_the_token_limit(self):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = datetime.now()
            token = self.user.auth_token_set.filter(Q(expiry__gt=now) & Q(last_use__gt=(now-knox_settings.LAST_USE_TO_EXPIRY)))
            print("here in check_exceeding_the_token_limit, token numbers = "+str(token.count()))
            print("here in check_exceeding_the_token_limit, token_limit_per_user = "+str(token_limit_per_user))
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return None

    def remove_axpired_token_user(self):
        now = datetime.now()
        self.user.auth_token_set.filter(Q(expiry__lte=now) | Q(last_use__lte=(now-knox_settings.LAST_USE_TO_EXPIRY))).delete()

    def post(self, request, format=None):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = datetime.now()
            token = request.user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        self.user = self.request.user
        instance, token = self.create_token()
        user_logged_in.send(sender=request.user.__class__,
                            request=request, user=request.user)
        data = self.get_post_response_data(request, token, instance)
        return Response(data)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutAllView(APIView):
    '''
    Log the user out of all sessions
    I.E. deletes all auth tokens for the user
    '''
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
