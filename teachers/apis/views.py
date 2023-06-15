from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.models import Course
from .permissions import IsTeacher, IsRelativeTeacherMixin


class TeacherHomeAPIView(GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        teacher = request.user.teacher_user
        now = timezone.now().date()
        day_next_week = (timezone.now() + timedelta(days=7)).date()
        courses = Course.objects.filter(
            teacher=teacher)
        week_sessions = Session.objects.filter(Q(date__gte=now) & Q(
            date__lte=day_next_week) & Q(course__in=courses))

        return Response({
            'courses': CourseSerializer(courses,  many=True).data,
            'sessions': SessionSerializer(week_sessions, many=True).data,
            "now": now
        },
            status=status.HTTP_200_OK
        )


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
