from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView

from students.apis.serializers import StudentRegisterSerializer

class StudentRegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentRegisterSerializer
    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail":"Ok"}, status=status.HTTP_201_CREATED)
