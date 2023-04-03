from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from accounts.api.serializers import \
    EmailSerializer,\
    EmailConfirmationCodeSerializer,\
    PasswordResetConfirmSerializer,\
    PasswordResetValidateCodeSerializer,\
    UserRegisterSerializer

from accounts.utils import setUp_user_email_confirmation, setUp_user_password_reset,\
    setUp_user_email_confirmation_complated, compare_stored_user_agent_data_and_request_user_agent_data,\
    setUp_user_password_reset_complated

from accounts.models import PasswordResetCode, EmailConfirmationCode, VERIFICATION_STATUS

User = get_user_model()


'''
for futue
دو تا کلاس گرفتن کد تایید برای ایمیل و ریست رمز عبور مشترکات زیادی دارن و تو دو سه نقطه با هم فرق دارن
serializer class, model, setUp function
'''

# ********** EMAIL CONFIRMATION
class EmailVerificationCodeRequestAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSerializer
    queryset = EmailConfirmationCode.objects.filter()
    def post(self, *args, **kwargs):
        emailSerializer = EmailSerializer(data=self.request.data)
        emailSerializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=emailSerializer.data.get("email"))
        except ObjectDoesNotExist:
            return Response({"message": "There is no user with the given email address"},status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({"message":"Your account is inactive"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        userEmailConfirmationCode = self.queryset.filter(user=user)
        
        if userEmailConfirmationCode.count()>0:
            userEmailConfirmationCode.order_by('-expire')
            currentEmailConfirmationCode = None
            for code in userEmailConfirmationCode:
                if not currentEmailConfirmationCode:
                    currentEmailConfirmationCode = code
                else:
                    code.delete()
            code_remainingـtime = currentEmailConfirmationCode.code_remainingـtime()
            if code_remainingـtime:
                return Response({"message": f"try in {code_remainingـtime} later"},status=status.HTTP_409_CONFLICT)
            else:
                currentEmailConfirmationCode.delete()
        
        if user.is_email_verified() :
            return Response({"message": "Your email was confirmed"},status=status.HTTP_400_BAD_REQUEST)
        result = setUp_user_email_confirmation(user, self.request)
        return Response({"message": result["message"]},status=result["status_code"])


class EmailVerificationConfirmAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailConfirmationCodeSerializer
    queryset = EmailConfirmationCode.objects.filter()
    def post(self, *args, **kwargs):
        confirmationCodeSerializer = self.serializer_class(data=self.request.data)
        confirmationCodeSerializer.is_valid(raise_exception=True)
        try:
            emailConfirmationCode = self.queryset.get(code=confirmationCodeSerializer.data.get("code"))
        except ObjectDoesNotExist:
            return Response({"message":"wrong code"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # Checking whether the request IP address or user agent data
        # is different from the what ever stored in the database for that code
        result = compare_stored_user_agent_data_and_request_user_agent_data(emailConfirmationCode, self.request)
        if result.get("status_code") != 200:
            return Response({"message": result["message"]},status=result["status_code"])
        
        if emailConfirmationCode.code_remainingـtime() is None:
            emailConfirmationCode.delete()
            return Response({"message":"code is expired"}, status=status.HTTP_400_BAD_REQUEST)
        user = emailConfirmationCode.user
        if user.is_email_verified():
            return Response({"message":"Your email was confirmed"}, status=status.HTTP_400_BAD_REQUEST)
        user.verification_status = user.verification_status * VERIFICATION_STATUS.EMAIL
        user.save()
        emailConfirmationCode.delete()
        setUp_user_email_confirmation_complated(user)
        return Response({"message":"Email has been successfully verified"}, status=status.HTTP_200_OK)


# ********** PASSWORD REST
class PasswordResetCodeRequestAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSerializer
    queryset = PasswordResetCode.objects.filter()
    def post(self, *args, **kwargs):
        emailSerializer = self.serializer_class(data=self.request.data)
        emailSerializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=emailSerializer.data.get("email"))
        except ObjectDoesNotExist:
            return Response({"message": "There is no user with the given email address"},status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({"message":"Your account is inactive"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        userPasswordResetCode = self.queryset.filter(user = user)
        
        if userPasswordResetCode:
            userPasswordResetCode.order_by('-created_at')
            currentPasswordResetCode = None
            for code in userPasswordResetCode:
                if not currentPasswordResetCode:
                    currentPasswordResetCode = code
                else:
                    code.delete()
            
            code_remainingـtime = currentPasswordResetCode.code_remainingـtime()
            if code_remainingـtime:
                return Response({"message": f"try in {code_remainingـtime} later"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                currentPasswordResetCode.delete()
        
        result = setUp_user_password_reset(user, self.request)
        return Response({"message": result["message"]},status=result["status_code"])


class ResetPasswordValidateTokenAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetValidateCodeSerializer
    queryset = PasswordResetCode.objects.filter()
    def post(self, *args, **kwargs):
        passwordResetProcessSerializer = self.serializer_class(data=self.request.data)
        passwordResetProcessSerializer.is_valid(raise_exception=True)
        try:
            code = passwordResetProcessSerializer.data.get("code")
            passwordResetCode = self.queryset.get(code=code)
        except ObjectDoesNotExist:
            return Response({"message":"code in wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
        if passwordResetCode.code_remainingـtime() is None:
            passwordResetCode.delete()
            return Response({"message":"code is expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = compare_stored_user_agent_data_and_request_user_agent_data(passwordResetCode, self.request)
        if result.get("status_code") != 200:
            return Response({"message": result["message"]},status=result["status_code"])
        
        return Response({"message":"OK"}, status=status.HTTP_100_CONTINUE)


class ResetPasswordConfirmAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    queryset = PasswordResetCode.objects.filter()
    def post(self, *args, **kwargs):
        passwordResetProcessSerializer = self.serializer_class(data=self.request.data)
        passwordResetProcessSerializer.is_valid(raise_exception=True)
        try:
            code = passwordResetProcessSerializer.data.get("code")
            passwordResetCode = self.queryset.get(code=code)
        except ObjectDoesNotExist:
            return Response({"message":"code in wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
        if passwordResetCode.code_remainingـtime() is None:
            passwordResetCode.delete()
            return Response({"message":"code is expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Checking whether the request IP address or user agent data
        # is different from the what ever stored in the database for that code
        result = compare_stored_user_agent_data_and_request_user_agent_data(passwordResetCode, self.request)
        if result.get("status_code") != 200:
            return Response({"message": result["message"]},status=result["status_code"])
        
        user = passwordResetCode.user
        password = passwordResetProcessSerializer.data.get("password1")
        user.set_password(password)
        user.save()
        passwordResetCode.delete()
        setUp_user_password_reset_complated(user)
        return Response({"status":"password reset was successful"}, status=status.HTTP_200_OK)


# from dj_rest_auth.registration import views
# from dj_rest_auth import views

class UserRegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    def post(self, *args, **kwargs):
        userRegisterSerializer = self.serializer_class(data=self.request.data)
        userRegisterSerializer.is_valid(raise_exception=True)
        userRegisterSerializer.save()
        return Response({"status":"Ok"}, status=status.HTTP_201_CREATED)
