from django.urls import path
from accounts.api import views
urlpatterns = [
    path('register/', views.UserRegisterAPIView.as_view(), name="user_register"),
    path('login/', views.UserLoginAPIView.as_view(), name="user_login"),
    path('logout/', views.LogoutView.as_view(), name='user_logout'),
    path('logout_all/', views.LogoutAllView.as_view(), name='user_logoutall'),
    path('email/verification/get_code/', views.EmailVerificationCodeRequestAPIView.as_view(), name="email_verification_request_code"),
    path('email/verification/confirm/', views.EmailVerificationConfirmAPIView.as_view(), name="email_verification_confirm"),
    path('password/reset/get_code/', views.PasswordResetCodeRequestAPIView.as_view(), name="password_reset_request_code"),
    path('password/reset/verify_code/', views.ResetPasswordVerifyCodeAPIView.as_view(), name="password_reset_verify_code"),
    path('password/reset/confirm/', views.ResetPasswordConfirmAPIView.as_view(), name="password_reset_confirm"),
    path('password/change/', views.PasswordChangeAPIView.as_view(), name="password_change")
]
