from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course
from courses.apis.serializers import SessionSerializer, CourseSerializer
from .serializers import StudentRegisterSerializer
from .permissions import IsStudent, IsRelativeStudentMixin
from ..models import StudentEnroll


class StudentRegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentRegisterSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Ok"}, status=status.HTTP_201_CREATED)


class StudentHomeAPIView(GenericAPIView):
    permission_classes = [IsStudent]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        student = request.user.student_user
        now = timezone.now().date()
        day_next_week = (timezone.now() + timedelta(days=7)).date()
        studentEnrolls_course = StudentEnroll.objects.filter(
            student=student).select_related('course').all()
        courses = [
            studentEnrolls_course.course for studentEnrolls_course in studentEnrolls_course]
        week_sessions = Session.objects.filter(Q(date__gte=now) & Q(
            date__lte=day_next_week) & Q(course__in=courses))
        return Response({
            'courses': CourseSerializer(courses,  many=True).data,
            'sessions': SessionSerializer(week_sessions, many=True).data,
            "now": now
        },
            status=status.HTTP_200_OK
        )


class StudentCourseDetailAPIView(IsRelativeStudentMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        sessions = Session.objects.filter(course=self.course).order_by('date')
        return Response({"sessions": SessionSerializer(sessions, many=True).data}, status=status.HTTP_200_OK)


class StudentSessionDetailAPIView(GenericAPIView):
    pass
