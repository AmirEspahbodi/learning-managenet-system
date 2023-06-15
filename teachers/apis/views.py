from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course
from courses.apis.serializers import SessionSerializer
from .permissions import IsTeacher, IsRelativeTeacherMixin


class TeacherCourseDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        sessions = Session.objects.filter(course=self.course).order_by('date')
        return Response({"sessions": SessionSerializer(sessions, many=True).data}, status=status.HTTP_200_OK)


class TeacherCourseStudentSettingAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class TeacherSessionDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
