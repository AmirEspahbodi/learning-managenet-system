from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_api.api_view import CreateAPIView
from .schema import SignupL1Schema


@method_decorator(csrf_exempt, name="dispatch")
class UserSignUpL1APIView(CreateAPIView[SignupL1Schema]):
    SCHEMA_CLASS = SignupL1Schema

    async def post(self, request):

        return JsonResponse(
            status=201,
            data=self.request_body_schema.model_dump(),
        )
