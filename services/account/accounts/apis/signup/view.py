from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction, IntegrityError

from rest_api import status
from rest_api.api_view import CreateAPIView
from utils.transaction import AsyncAtomicContextManager

from .schema import SignupL1Schema, UserSchema
from accounts.models import User, UserExtra
from accounts.utils import get_user_ip, get_user_agent


@method_decorator(csrf_exempt, name="dispatch")
class UserSignUpL1APIView(CreateAPIView[SignupL1Schema]):
    SCHEMA_CLASS = SignupL1Schema

    async def post(self, request, *args, **kwargs):
        # create user
        try:
            async with AsyncAtomicContextManager():
                user = await User.objects.acreate(
                    password=User.set_password(self.request_body_schema.password1),
                    first_name=self.request_body_schema.first_name,
                    last_name=self.request_body_schema.last_name,
                    email=self.request_body_schema.email,
                    username=self.request_body_schema.username,
                    phone_number=self.request_body_schema.phone_number,
                )
                await UserExtra.objects.acreate(
                    user=user,
                    ip_address=get_user_ip(request),
                    user_agent=get_user_agent(request),
                )
        except BaseException:
            return JsonResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"error": "internal server error"},
            )

        return JsonResponse(
            status=status.HTTP_201_CREATED,
            data=UserSchema.model_validate(user).model_dump(),
        )
