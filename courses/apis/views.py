from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Course
from .serializers import CourseSerializer, CourseDetailSerializer

class CourseSearchAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        course_title = request.query_params.get('title')
        group_course_number = request.query_params.get('group_course_number')
        semester = request.query_params.get('semester')
        teacher_first_name = request.query_params.get('teacher_first_name')
        teacher_last_name = request.query_params.get('teacher_last_name')
        courses = Course.objects.filter(
            Q(course_title__title=course_title)
        )
        if group_course_number:
            courses = courses.filter(group_course_number=group_course_number)
        if semester:
            courses = courses.filter(semester=semester)
        if teacher_first_name:
            courses = courses.filter(teacher__user__first_name=teacher_first_name)
        if teacher_last_name:
            courses = courses.filter(teacher__user__last_name=teacher_last_name)
        return Response(CourseSerializer(courses, many=True).data, status=status.HTTP_200_OK)


class CourseSearchDetailAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        content = CourseDetailSerializer(course).data
        return Response(content, status=status.HTTP_200_OK)
