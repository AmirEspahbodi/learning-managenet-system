from django.urls import path
from accounts.api import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name="user_register"),
    path('email/verification/get_code/', views.EmailVerificationCodeRequestAPIView.as_view(), name="email_verification_request_code"),
    path('email/verification/confirm/', views.EmailVerificationConfirmAPIView.as_view(), name="email_verification_confirm"),
    path('password/reset/', views.PasswordResetCodeRequestAPIView.as_view(), name="password_reset_request_code"),
    path('password/reset/validate/', views.ResetPasswordValidateTokenAPIView.as_view(), name="password_reset_validate_code"),
    path('password/reset/confirm/', views.ResetPasswordConfirmAPIView.as_view(), name="password_reset_confirm")
]
