from django.urls import path
from accounts.apis import views

urlpatterns = [
    path("token_status/", views.AuthTokenVarifyApiView.as_view(), name="token_status"),
    path("signup_l1/", views.UserRegisterL1APIView.as_view(), name="user_register_l1"),
    path("signup_l2/", views.UserRegisterL2APIView.as_view(), name="user_register_l1"),
    path("login/", views.UserLoginAPIView.as_view(), name="user_login"),
    path("logout/", views.LogoutView.as_view(), name="user_logout"),
    path("logout_all/", views.LogoutAllView.as_view(), name="user_logoutall"),
    path("token/verify/", views.VerifyToken.as_view(), name="varify_token"),
    path(
        "email/verification/get_code/",
        views.EmailVerificationCodeRequestAPIView.as_view(),
        name="email_verification_request_code",
    ),
    path(
        "email/verification/confirm/",
        views.EmailVerificationConfirmAPIView.as_view(),
        name="email_verification_confirm",
    ),
    path(
        "password/reset/get_code/",
        views.PasswordResetCodeRequestAPIView.as_view(),
        name="password_reset_request_code",
    ),
    path(
        "password/reset/verify_code/",
        views.ResetPasswordVerifyCodeAPIView.as_view(),
        name="password_reset_verify_code",
    ),
    path(
        "password/reset/confirm/",
        views.ResetPasswordConfirmAPIView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/change/",
        views.PasswordChangeAPIView.as_view(),
        name="password_change",
    ),
]
