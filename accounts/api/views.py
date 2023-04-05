from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.authtoken.models import AuthToken
from accounts.authtoken import views as knoxViews
from accounts.api.serializers import \
    EmailSerializer,\
    EmailConfirmationCodeSerializer,\
    PasswordResetConfirmSerializer,\
    PasswordResetValidateCodeSerializer,\
    UserRegisterSerializer,\
    UserLoginSerializer


from accounts.utils import setUp_user_email_confirmation, setUp_user_password_reset,\
    setUp_user_email_confirmation_complated, compare_stored_user_agent_data_and_request_user_agent_data,\
    setUp_user_password_reset_complated

from accounts.models import PasswordResetCode, EmailConfirmationCode, VERIFICATION_STATUS

UserModel = get_user_model()


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
            user = UserModel.objects.get(email=emailSerializer.data.get("email"))
        except ObjectDoesNotExist:
            return Response({"message": "There is no user with the given email address"},status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({"message":"Your account is inactive"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        userEmailConfirmationCode = self.queryset.filter(user=user)
        
        if userEmailConfirmationCode.count()>0:
            userEmailConfirmationCode.order_by('-created_at')
            currentEmailConfirmationCode = None
            for code in userEmailConfirmationCode:
                if not currentEmailConfirmationCode:
                    currentEmailConfirmationCode = code
                else:
                    code.delete()
            code_remaining_time = currentEmailConfirmationCode.code_remaining_time()
            if code_remaining_time:
                return Response({"message": f"try in {int(code_remaining_time.seconds/60)} minutes and {code_remaining_time.seconds%60} seconds later"},status=status.HTTP_409_CONFLICT)
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
        
        if emailConfirmationCode.code_remaining_time() is None:
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
            user = UserModel.objects.get(email=emailSerializer.data.get("email"))
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
            
            code_remaining_time = currentPasswordResetCode.code_remaining_time()
            if code_remaining_time:
                return Response({"message": f"try in {int(code_remaining_time.seconds/60)} minutes and {code_remaining_time.seconds%60} seconds later"}, status=status.HTTP_409_CONFLICT)
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
        
        if passwordResetCode.code_remaining_time() is None:
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
        
        if passwordResetCode.code_remaining_time() is None:
            passwordResetCode.delete()
            return Response({"message":"code is expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Checking whether the request IP address or user agent data
        # is different from the what ever stored in the database for that code
        result = compare_stored_user_agent_data_and_request_user_agent_data(passwordResetCode, self.request)
        if result.get("status_code") != 200:
            return Response({"message": result["message"]},status=result["status_code"])
        
        user = passwordResetCode.user
        password = passwordResetProcessSerializer.data.get("password1")
        if user.check_password(password):
            return Response({"message":"The new password must not be the same as the previous password"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()
        AuthToken.objects.filter(user=user).delete()
        passwordResetCode.delete()
        setUp_user_password_reset_complated(user)
        return Response({"status":"password reset was successful"}, status=status.HTTP_200_OK)


class UserRegisterAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    def post(self, *args, **kwargs):
        userRegisterSerializer = self.serializer_class(data=self.request.data)
        userRegisterSerializer.is_valid(raise_exception=True)
        userRegisterSerializer.save()
        return Response({"status":"Ok"}, status=status.HTTP_201_CREATED)


class UserLoginAPIView(knoxViews.LoginView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post (self, *args, **kwargs):
        self.userLoginSerializer = self.serializer_class(data=self.request.data)
        self.userLoginSerializer.is_valid(raise_exception=True)
        self.user = self.userLoginSerializer.validated_data.get("user")
        
        re = self.check_exceeding_the_token_limit()
        if re:
            return re
        
        self.remove_axpired_token_user()

        instance, token = self.create_token()
        
        data = self.get_post_response_data(self.request, token, instance)

        return Response(data, status=status.HTTP_200_OK)


class IsUserAuthenticated(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, *args, **kwargs):
        return Response({"yes you are!"})