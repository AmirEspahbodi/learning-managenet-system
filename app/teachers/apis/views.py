from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsTeacher, IsRelativeTeacherMixin
from .serialisers import StudentAccessSerializer
from students.models import Student


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


class TeacherCourseSettingGetStudentsAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = StudentAccessSerializer

    # def get(self, request, *args, **kwargs):
    #     studentEnrools = StudentEnroll.objects.filter(course=self.course)
    #     return Response(StudentEnrollSerializer(studentEnrools, many=True).data, status=status.HTTP_200_OK)

    # def put(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     student = Student.objects.get(
    #         user__id=serializer.data.get('student_id'))
    #     self.course
    #     try:
    #         studentEnroll = StudentEnroll.objects.get(
    #             course=self.course, student=student)
    #     except ObjectDoesNotExist:
    #         return Response({}, status=status.HTTP_403_FORBIDDEN)
    #     studentEnroll.is_student_access = serializer.data.get('access')
    #     studentEnroll.save()
    #     return Response({"access": studentEnroll.is_student_access}, status=status.HTTP_200_OK)


class TeacherSessionDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
