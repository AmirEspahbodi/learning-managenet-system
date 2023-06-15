from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q
from rest_framework.serializers import DateTimeField
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from ..app_settings import account_settings
from ..authtoken.app_settings import token_settings
from ..authtoken.auth import TokenAuthentication
from .permissions import AllowAnyAuthentication
from accounts import utils

UserModel = get_user_model()


class VerifyVerificationCodeMixin:
    def verify_verification_code(self, code=None, verificationCode=None, delete_code=False):
        if not verificationCode:
            try:
                verificationCode = self.queryset.get(code=code)
            except ObjectDoesNotExist:
                return {
                    "detail": "wrong code",
                    "status_code": status.HTTP_406_NOT_ACCEPTABLE
                }
            if verificationCode.code_remaining_time() is None:
                verificationCode.delete()
                return {"detail": "code is expired", "status_code": status.HTTP_400_BAD_REQUEST}

        # Checking whether the request IP address or user agent data
        # is different from the what ever stored in the database for that code
        result = utils.compare_user_agents_data(verificationCode, self.request)
        if result.get("status_code") != 200:
            return {"detail": result["detail"], "status_code": result["status_code"]}
        self.user = verificationCode.user
        if delete_code:
            verificationCode.delete()
            return {'detail': 'code is ok', 'status_code': 200}
        return {'detail': 'code is ok', 'status_code': 200}


class CreateTokenMixin:
    def get_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_token_ttl(self):
        return token_settings.TOKEN_TTL

    def get_token_prefix(self):
        return token_settings.TOKEN_PREFIX

    def get_token_limit_per_user(self):
        return token_settings.TOKEN_LIMIT_PER_USER

    def get_expiry_datetime_format(self):
        return token_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def create_token(self):
        instance, token = token_settings.MODELS.AUTH_TOKEN.objects.create(
            user=self.user,
            prefix=self.get_token_prefix()
        )
        (client_ip, is_routable, user_agent_data) = utils.get_ip_and_user_agent(
            self.request)
        token_settings.MODELS.AUTH_TOKEN_INFORMATION.objects.create(
            authToken=instance,
            ip_address=client_ip if client_ip else is_routable,
            user_agent=user_agent_data,
        )
        user_logged_in.send(sender=self.user.__class__,
                            request=self.request, user=self.user)
        return instance, token

    def get_post_response_data(self):
        instance, token = self.create_token()
        return {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'last_use_to_expire': {
                'seconds': token_settings.LAST_USE_TO_EXPIRY.seconds,
                'days': token_settings.LAST_USE_TO_EXPIRY.days
            },
            'token': token
        }


# ********** EMAIL VERIFICATION
class EmailVerificationCodeRequestAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = account_settings.SERIALIZERS.EMAIL
    queryset = account_settings.MODELS.EMAIL_VERIFICATION_CODE.objects.filter()
    authentication_classes = [AllowAnyAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserModel.objects.get(email=serializer.data.get("email"))
        except ObjectDoesNotExist:
            return Response({"detail": _("There is no user with the given email address")}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"detail": _("Your account is inactive")}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if user.is_email_verified():
            return Response({"detail": _("Your email was verified")}, status=status.HTTP_400_BAD_REQUEST)

        result = utils.setUp_user_email_verification_code(user, request)
        return Response(*result)


class EmailVerificationConfirmAPIView(GenericAPIView, VerifyVerificationCodeMixin):
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.EMAIL_VERIFICATION_CODE
    queryset = account_settings.MODELS.EMAIL_VERIFICATION_CODE.objects.filter()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get("code")
        result = self.verify_verification_code(code, delete_code=True)
        if result['status_code'] == 200:
            if self.user.is_email_verified():
                return Response({"detail": _("Your email was confirmed")}, status=status.HTTP_400_BAD_REQUEST)
            self.user.verification_status = self.user.verification_status * \
                account_settings.MODELS.VERIFICATION_STATUS.EMAIL
            self.user.save()
            utils.setUp_user_email_verification_complated(self.user)
            return Response({"detail": _("Email has been successfully verified")}, status=status.HTTP_200_OK)
        return Response({"detail": result["detail"]}, status=result['status_code'])


# ********** PASSWORD REST
class PasswordResetCodeRequestAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.EMAIL
    queryset = account_settings.MODELS.PASSWORD_RESET_CODE.objects.filter()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserModel.objects.get(email=serializer.data.get("email"))
        except ObjectDoesNotExist:
            return Response({"detail": _("There is no user with the given email address")}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"detail": _("Your account is inactive")}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if not user.is_email_verified():
            return Response({"detail": _("E-mail is not verified!")}, status=status.HTTP_406_NOT_ACCEPTABLE)

        result = utils.setUp_user_password_reset_verification_code(
            user, request)
        return Response(*result)


class ResetPasswordVerifyCodeAPIView(GenericAPIView, VerifyVerificationCodeMixin):
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.PASWORD_RESET_VERIFY_CODE
    queryset = account_settings.MODELS.PASSWORD_RESET_CODE.objects.filter()

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get("code")
        result = self.verify_verification_code(code=code)
        return Response(
            {"detail": result['detail']},
            status=result['status_code']
        )


class ResetPasswordConfirmAPIView(APIView, VerifyVerificationCodeMixin):
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.PASSWORD_RESET_CONFIRM
    queryset = account_settings.MODELS.PASSWORD_RESET_CODE.objects.filter()

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        verificationCode = serializer.validated_data.get("verificationCode")
        print("after serializer validation = "+str(verificationCode.code))
        result = self.verify_verification_code(
            verificationCode=verificationCode)
        if result['status_code'] == 200:
            password = serializer.data.get("new_password1")
            if self.user.check_password(password):
                return Response(
                    {
                        "detail": _("The new password must not be the same as the previous password")},
                    status=status.HTTP_409_CONFLICT
                )
            self.user.set_password(password)
            self.user.save()
            verificationCode.delete()
            token_settings.MODELS.AUTH_TOKEN.objects.filter(
                user=self.user).delete()
            utils.setUp_user_password_reset_complated(self.user)
            result['detail'] = "password reset was successful"
        return Response({"detail": result['detail']}, status=result['status_code'])


# ********** PASSWORD CHANGE
class PasswordChangeAPIView(APIView, CreateTokenMixin):
    '''
    if it complite successfully, it will return new token and expire information
    '''
    serializer_class = account_settings.SERIALIZERS.PASSWORD_CHANGE
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        password = serializer.data.get("new_password1")
        self.user = request.user
        if self.user.check_password(password):
            return Response({"detail": _("The new password must not be the same as the previous password")}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(password)
        request.user.save()
        if account_settings.LOGOUT_ON_PASSWORD_CHANGE:
            token_settings.MODELS.AUTH_TOKEN.objects.filter(
                user=request.user).delete()
            return Response({'detail': _('New password has been saved. you need to login again')})
        else:
            token_settings.MODELS.AUTH_TOKEN.objects.filter(
                user=request.user).delete()
            data = self.get_post_response_data()
            return Response(data, status=status.HTTP_200_OK)


# ********** AUTH
class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.USER_REGISTER

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Ok"}, status=status.HTTP_201_CREATED)


class UserLoginAPIView(APIView, CreateTokenMixin):
    permission_classes = (AllowAny,)
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = account_settings.SERIALIZERS.USER_LOGIN

    def check_exceeding_the_token_limit(self):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = self.user.auth_token_set.filter(Q(expiry__gt=now) & Q(
                last_use__gt=(now-token_settings.LAST_USE_TO_EXPIRY)))
            if token.count() >= token_limit_per_user:
                return Response(
                    {"non_field_errors": [
                        "Maximum amount of tokens allowed per user exceeded."]},
                    status=status.HTTP_403_FORBIDDEN
                )
        return None

    def remove_expired_token_user(self):
        now = timezone.now()
        self.user.auth_token_set.filter(
            Q(expiry__lte=now) | Q(last_use__lte=(
                now-token_settings.LAST_USE_TO_EXPIRY))
        ).delete()

    def get_post_response_data(self):
        return {
            "user_id": self.user.id,
            "username": self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            ** super().get_post_response_data(),
        }

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.user = serializer.validated_data.get("user")

        if not self.user.is_email_verified():
            return Response({"non_field_errors": ["EMAIL_VERIFICATION"]}, status=403)

        self.remove_expired_token_user()
        re = self.check_exceeding_the_token_limit()
        if re:
            return re

        data = self.get_post_response_data()

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response({'status': 'ok'}, status=status.HTTP_204_NO_CONTENT)


class LogoutAllView(APIView):
    '''
    Log the user out of all sessions
    I.E. deletes all auth tokens for the user
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response({'status': 'ok'}, status=status.HTTP_204_NO_CONTENT)


class VerifyToken(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)


class AuthTokenVarifyApiView(APIView):

    permission_classes = (AllowAny,)
    authentication_classes = [AllowAnyAuthentication]
    serializer_class = token_settings.SERIALIZERS.AUTH_TOKEN

    def get_expiry_datetime_format(self):
        return token_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get('token')
        try:
            _, authtoken = TokenAuthentication().authenticate_credentials(token)
        except exceptions.AuthenticationFailed as e:
            return Response({'details': e.detail}, status=status.HTTP_401_UNAUTHORIZED)
        remain_time = authtoken.expiry - timezone.now()
        ttu = token_settings.LAST_USE_TO_EXPIRY
        return Response(
            {
                'expiry': self.format_expiry_datetime(authtoken.expiry),
                'last_use_to_expire': {
                    'seconds': token_settings.LAST_USE_TO_EXPIRY.seconds, 'days': token_settings.LAST_USE_TO_EXPIRY.days},
                'token': token
            },
            status=status.HTTP_200_OK
        )


# ********** GetGlobal Settings
class GetMobileGlobalSettingsApiView(APIView):
    serializer_class = account_settings.SERIALIZERS.Mobile_Global_Settings

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class({
            "logout_on_exit": True,
            "auth_token_last_use_to_expire": {
                'days': token_settings.LAST_USE_TO_EXPIRY.days,
                'seconds': token_settings.LAST_USE_TO_EXPIRY.seconds
            }
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
