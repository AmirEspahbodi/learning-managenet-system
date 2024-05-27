import sys
import json

from accounts.mail import BaseEmailMessage

if sys.version_info[0] == 3:
    text_type = str
from django.contrib.sites.models import Site
from django.conf import settings
from accounts.app_settings import account_settings


# from django.utils.exceptions import ObjectDoesNotExist
# from django.utils.http import urlsafe_base64_encode
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import force_bytes
# V0: token web base (no db)
# class AcconutActivationToken(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp: int):
#         return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.credit_level))
# class ActivationEmail1(BaseEmailMessage):
#     template_name = 'accounts/email_activations.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = context.get('user')
#         context['web_server_port'] = 8000 if settings.DEBUG else 80
#         context['user'] = user
#         context['uid'] = urlsafe_base64_encode(force_bytes(user.pk))
#         context['token'] = AcconutActivationToken().make_token(user)
#         context['site_name'] = Site.objects.get_current().name
#         context['domain']= Site.objects.get_current().domain
#         return context

# V1: token web base (stored in db)


class ActivationEmailV1(BaseEmailMessage):
    template_name = "accounts/email/email_activationsV1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_server_port"] = 8000 if settings.DEBUG else 80
        context["site_name"] = Site.objects.get_current().name
        context["domain"] = Site.objects.get_current().domain
        return context


class PasswordResetEmailV1(BaseEmailMessage):
    template_name = "accounts/password/password_resetV1.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["web_server_port"] = 8000 if settings.DEBUG else 80
        context["site_name"] = Site.objects.get_current().name
        context["domain"] = Site.objects.get_current().domain
        return context


class ActivationEmailCompletedEmail(BaseEmailMessage):
    template_name = "accounts/email/email_activations_complated.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = Site.objects.get_current().name
        return context


class PasswordResetCompletedEmail(BaseEmailMessage):
    template_name = "accounts/password/password_reset_complated.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["site_name"] = Site.objects.get_current().name
        return context


def setUp_user_password_resetV1(user):
    new_password_token = account_settings.MODELS.PASSWORD_RESET_CODE(user=user)
    new_password_token.save()
    PasswordResetEmailV1(
        context={"user": user, "token": new_password_token.token}
    ).send(to=[user.email])


def setup_user_email_verification_complated(user):
    ActivationEmailCompletedEmail().send(to=[user.email])


def setup_user_password_reset_complated(user):
    PasswordResetCompletedEmail().send(to=[user.email])


# V2: api base (Six digit code)
class ActivationEmail(BaseEmailMessage):
    template_name = "accounts/email/email_activations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = Site.objects.get_current().name
        return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = "accounts/password/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["site_name"] = Site.objects.get_current().name
        return context


def compare_user_agents_data(codeInstance, request):
    """
    Checking whether the request IP address or user agent data
    is different from the what ever stored in the database for that code
    """
    current_client_ip, current_is_routable, current_user_agent_data = (
        get_ip_and_user_agent(request) if request else (None, None, None)
    )

    storred_client_ip, storred_user_agent_data = (
        codeInstance.ip_address,
        json.loads(codeInstance.user_agent.replace("'", '"')),
    )

    if not (
        storred_client_ip == current_client_ip
        or storred_client_ip == current_is_routable
    ):
        return {
            "detail": "do not change your ip address during process",
            "status_code": 403,
        }

    if (
        current_user_agent_data["get_browser"] != storred_user_agent_data["get_browser"]
        or current_user_agent_data["get_device"]
        != storred_user_agent_data["get_device"]
        or current_user_agent_data["get_os"] != storred_user_agent_data["get_os"]
    ):
        return {
            "detail": "do not change your browser during process",
            "status_code": 403,
        }

    return {"detail": "OK", "status_code": 200}


def generate_new_verification_code(VerificationCode, user, request=None):
    """
    get request ip addr and user_agent data and generate a 6 digit code.
    store code and these information in datebase and send code to user via email addres.
    return proccess result.
    """
    client_ip, is_routable, user_agent_data = (
        get_ip_and_user_agent(request) if request else (None, None, None)
    )
    code = VerificationCode.generate_verification_code()
    if code == 0:
        """
        If the function fails to generate a six-digit code, it means that most of the digits in the range are reserved
        try to remove expire codes and return one of the deleted code
        """
        from accounts.models import delete_expired_codes

        code = delete_expired_codes(VerificationCode)
        """
        if there is no expired code we must tell user try again later!
        """
        if code == 0:
            return {
                "detail": "most of the codes are reserved! Try in a few minutes later",
                "status_code": 409,
            }

    verificationCode = VerificationCode(
        user=user,
        code=code,
        ip_address=(
            client_ip if client_ip else is_routable if is_routable else "private"
        ),
        user_agent=user_agent_data if user_agent_data else "{}",
    )
    verificationCode.save()
    return verificationCode


def check_existing_user_verification_codes(VerificationCode, user):
    verificationCode = VerificationCode.objects.filter(user=user).order_by(
        "-created_at"
    )
    if verificationCode.count() > 0:
        currentVerificationCode = None
        for code in verificationCode:
            if not currentVerificationCode:
                currentVerificationCode = code
            else:
                code.delete()
        remain_time = currentVerificationCode.code_remaining_time()
        if remain_time:
            if (
                currentVerificationCode.resended
                < account_settings.VERIFICATION_CODE_RESEND_LIMIT
            ):
                currentVerificationCode.resended = currentVerificationCode.resended + 1
                currentVerificationCode.save()
                return currentVerificationCode
            else:
                return (
                    {
                        "detail": "too much requests!",
                        "time": {
                            "hours": int(remain_time.seconds / 3600),
                            "minutes": int((remain_time.seconds / 60) % 60),
                            "seconds": int(remain_time.seconds % 60),
                        },
                    },
                    429,  # HTTP_429_TOO_MANY_REQUESTS
                )
        else:
            currentVerificationCode.delete()
            return None
    return None


def setup_user_verification_code(VerificationCode, Email, user, request):
    """
    check if there is a existing verification code
        if it's not expired
            if it not reached resend number, resend it
            else tell user wait to get new code
        elSe its expired delete it
    else there is not code, generate code and send it
    """
    result = check_existing_user_verifivation_codes(VerificationCode, user)
    if isinstance(result, tuple):
        return result
    if result is None:
        result = generate_new_verification_code(VerificationCode, user, request)

    Email(context={"user": user, "code": result.code}).send(to=[user.email])
    remain_time = result.code_remaining_time()
    print(remain_time)
    return (
        {
            "detail": "The code has been sent to your email address",
            "time": {
                "hours": int(remain_time.seconds / 3600),
                "minutes": int((remain_time.seconds / 60) % 60),
                "seconds": int(remain_time.seconds % 60),
            },
        },
        200,
    )
