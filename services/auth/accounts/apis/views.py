from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse


@method_decorator(csrf_exempt, name="dispatch")
class UserRegisterL1APIView(View):
    def post(self, request):
        return JsonResponse(status=201, data={"user_id": "1"})
