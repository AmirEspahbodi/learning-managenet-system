from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import Course
from .serializers import CourseSerializer, CourseDetailSerializer


class CourseSearchAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CourseSerializer

    def get(self, request, *args, **kwargs):
        search_content = request.query_params.get("content")
        if search_content is None:
            courses = Course.objects.all()
            return Response(
                CourseSerializer(courses, many=True).data, status=status.HTTP_200_OK
            )
        courses = Course.objects.all()
        return Response(
            CourseSerializer(courses, many=True).data, status=status.HTTP_200_OK
        )


class CourseSearchDetailAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        content = CourseDetailSerializer(
            course,
            context={
                "course_id": course_id,
                "is_student": hasattr(request.user, "student_user"),
                "user_id": request.user.id,
            },
        ).data
        return Response(content, status=status.HTTP_200_OK)
