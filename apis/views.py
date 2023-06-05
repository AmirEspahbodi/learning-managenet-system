from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class CheckConnection(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)
