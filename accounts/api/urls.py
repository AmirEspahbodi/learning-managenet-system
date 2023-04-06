from django.urls import path
from accounts.api import views
from accounts.authtoken import views as knoxViews
urlpatterns = [
    path('is_authenticated/', views.IsUserAuthenticated.as_view()),
    path('register/', views.UserRegisterAPIView.as_view(), name="user_register"),
    path('login/', views.UserLoginAPIView.as_view(), name="user_login"),
    path('logout/', knoxViews.LogoutView.as_view(), name='knox_logout'),
    path('logout_all/', knoxViews.LogoutAllView.as_view(), name='knox_logout'),
    path('email/verification/get_code/', views.EmailVerificationCodeRequestAPIView.as_view(), name="email_verification_request_code"),
    path('email/verification/confirm/', views.EmailVerificationConfirmAPIView.as_view(), name="email_verification_confirm"),
    path('password/reset/get_code/', views.PasswordResetCodeRequestAPIView.as_view(), name="password_reset_request_code"),
    path('password/reset/verify_code/', views.ResetPasswordVerifyCodeAPIView.as_view(), name="password_reset_verify_code"),
    path('password/reset/confirm/', views.ResetPasswordConfirmAPIView.as_view(), name="password_reset_confirm")
]
