from django.db.models import Q, FilteredRelation
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import Course
from students.models import StudentEnroll
from .serializers import CourseSerializer, CourseDetailSerializer
from courses.permissions import IsStudent


class CourseSearchAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        course_title = request.query_params.get('course_title')
        group_course_number = request.query_params.get('group_course_number')
        semester = request.query_params.get('semester')
        courses = Course.objects.filter(
            course_title__title=course_title
        )
        if group_course_number:
            courses = courses.filter(group_course_number=group_course_number)
        if semester:
            courses = courses.filter(semester=semester)
        return Response(CourseSerializer(courses, many=True).data, status=status.HTTP_200_OK)


class CourseSearchDetailAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student = request.user.student_user if hasattr(
            request.user, "student_user") else None
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        content = CourseDetailSerializer(
            course, context={'student': student}).data
        return Response(content, status=status.HTTP_200_OK)


class CourseEnrollAPIView(GenericAPIView):
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        student = request.user.student_user
        course = get_object_or_404(Course, pk=course_id)
        studentEnrollExist = StudentEnroll.objects.exists(
            course=course, student=student)
        if not studentEnrollExist:
            return Response({"detail": "you already enrolled"}, status=status.HTTP_409_CONFLICT)
        StudentEnroll.objects.create(
            course=course, student=student)
        return Response({"detail", "ok"}, status=status.HTTP_200_OK)
