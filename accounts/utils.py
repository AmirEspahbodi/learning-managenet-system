from ipware import get_client_ip
from user_agents import parse
import sys
import json
from hashlib import md5
if sys.version_info[0] == 3:
    text_type = str
else:
    text_type = unicode
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.models import Site
# from django.utils.http import urlsafe_base64_encode 
# from django.utils.encoding import force_bytes
from django.conf import settings
from templated_mail.mail import BaseEmailMessage
# from django.core.exceptions import ObjectDoesNotExist
from accounts.models import EmailConfirmationCode, PasswordResetCode, generate_confirmation_code

    
############## V0: token web base (no db)
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

############## V1: token web base (stored in db)
class ActivationEmailV1(BaseEmailMessage):
    template_name = 'accounts/email/email_activationsV1.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['web_server_port'] = 8000 if settings.DEBUG else 80
        context['site_name'] = Site.objects.get_current().name
        context['domain']= Site.objects.get_current().domain
        return context

class PasswordResetEmailV1(BaseEmailMessage):
    template_name = "accounts/password/password_resetV1.html"
    def get_context_data(self):
        context = super().get_context_data()
        context['web_server_port'] = 8000 if settings.DEBUG else 80
        context['site_name'] = Site.objects.get_current().name
        context['domain']= Site.objects.get_current().domain
        return context


class ActivationEmailComplatedEmail(BaseEmailMessage):
    template_name = 'accounts/email/email_activations_complated.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = Site.objects.get_current().name
        return context


class PasswordResetComplatedEmail(BaseEmailMessage):
    template_name = "accounts/password/password_reset_complated.html"
    def get_context_data(self):
        context = super().get_context_data()
        context['site_name'] = Site.objects.get_current().name
        return context

def setUp_user_password_resetV1(user):
    new_password_token = PasswordResetCode(user=user)
    new_password_token.save()
    PasswordResetEmailV1(
        context={
            'user':user,
            'token': new_password_token.token
        }
    ).send(to=[user.email])

def setUp_user_email_confirmation_complated(user):
    ActivationEmailComplatedEmail(
    ).send(to=[user.email])

def setUp_user_password_reset_complated(user):
    PasswordResetComplatedEmail(
    ).send(to=[user.email])


################ V2: api base (Six digit code)
class ActivationEmail(BaseEmailMessage):
    template_name = 'accounts/email/email_activations.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = Site.objects.get_current().name
        return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = "accounts/password/password_reset.html"
    def get_context_data(self):
        context = super().get_context_data()
        context['site_name'] = Site.objects.get_current().name
        return context


def get_user_agent(request):
    if not hasattr(request, 'META'):
        return ''
    ua_string = request.META['HTTP_USER_AGENT']
    if not isinstance(ua_string, text_type):
        ua_string = ua_string.decode('utf-8', 'ignore')
    user_agent = parse(ua_string)
    user_agent_data = {
        "get_browser":str(user_agent.get_browser()),
        "get_device":str(user_agent.get_device()),
        "get_os":str(user_agent.get_os()),
        
        "is_bot":str(user_agent.is_bot),
        "is_email_client":str(user_agent.is_email_client),
        "is_mobile":str(user_agent.is_mobile),
        "is_pc":str(user_agent.is_pc),
        "is_tablet":str(user_agent.is_tablet),
        "is_touch_capable":str(user_agent.is_touch_capable),
    }
    return user_agent_data

def get_ip_and_user_agent(request):
    client_ip, is_routable, user_agent_data = None, None, None
    client_ip, is_routable = get_client_ip(request)
    user_agent_data = get_user_agent(request)
    
    return (client_ip, is_routable, user_agent_data)

def compare_stored_user_agent_data_and_request_user_agent_data(codeInstance, request):
    """
    Checking whether the request IP address or user agent data
    is different from the what ever stored in the database for that code
    """
    current_client_ip, current_is_routable, current_user_agent_data = get_ip_and_user_agent(request) if request else (None, None, None)

    storred_client_ip , storred_user_agent_data = (codeInstance.ip_address, json.loads(codeInstance.user_agent.replace("\'", "\"")))

    if not (storred_client_ip == current_client_ip or storred_client_ip==current_is_routable):
        return {"message":"do not change your ip address during process", "status_code":403}
    
    if  current_user_agent_data["get_browser"] != storred_user_agent_data["get_browser"] or \
        current_user_agent_data["get_device"] != storred_user_agent_data["get_device"] or \
        current_user_agent_data["get_os"] != storred_user_agent_data["get_os"] :
        return {"message":"do not change your browser during process", "status_code":403}

    return {"massaga":"OK", "status_code":200}


def setUp_user_email_password_confirmation(ConfirmationCode, Email, user, request):
    """
    get request ip addr and user_agent data and generate a 6 digit code.
    store code and these information in datebase and send code to user via email addres.
    return proccess result.
    """
    client_ip, is_routable, user_agent_data = get_ip_and_user_agent(request) if request else (None, None, None)
    code = generate_confirmation_code(ConfirmationCode)
    if code==0:
        """
        If the function fails to generate a six-digit code, it means that most of the digits in the range are reserved
        try to remove expire codes and return one of the deleted code
        """
        from accounts.models import delete_expired_codes
        code = delete_expired_codes(ConfirmationCode)
        """
        if there is no expired code we must tell user try again later!
        """
        if code==0:
            return {
                "message": "Try in a few minutes",
                "status_code": 409
            }

    confirmationCode = ConfirmationCode(
        user=user,
        code=code,
        ip_address= client_ip if client_ip else is_routable if is_routable else "private",
        user_agent= user_agent_data if user_agent_data else '{}'
    )
    confirmationCode.save()
    Email(
        context={
            'user':user,
            'code': confirmationCode.code
        }
    ).send(to=[user.email])
    return {
        "message":"The code has been sent to your email address",
        "status_code": 200
    }


def setUp_user_email_confirmation(user, request=None):
    return setUp_user_email_password_confirmation(EmailConfirmationCode, ActivationEmail, user, request)


def setUp_user_password_reset(user, request=None):
    return setUp_user_email_password_confirmation(PasswordResetCode, PasswordResetEmail, user, request)
