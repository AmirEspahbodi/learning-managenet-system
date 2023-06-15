from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course
from courses.apis.serializers import SessionSerializer
from .permissions import IsTeacher, IsRelativeTeacherMixin


class TeacherCourseDetailAPIView(GenericAPIView, IsRelativeTeacherMixin):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):

        course_id = kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)

        if not self.isRelativeTeacer(request, course):
            return Response({"message": "forbiden"}, status=status.HTTP_403_FORBIDDEN)

        sessions = Session.objects.filter(course=course).order_by('date')
        return Response({"sessions": SessionSerializer(sessions, many=True).data}, status=status.HTTP_200_OK)


class TeacherCourseStudentsAPIView(GenericAPIView, IsRelativeTeacherMixin):
    permission_classes = [IsTeacher]
