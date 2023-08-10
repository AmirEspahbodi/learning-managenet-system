from django.db.models import Q, FilteredRelation
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import Course, MemberShip, MemberShipRoles
from students.models import StudentEnroll
from .serializers import CourseSerializer, CourseDetailSerializer
from courses.permissions import IsStudent


class CourseSearchAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        operator: str = request.query_params.get("operator") or "and"
        q_operator = (
            Q.OR
            if operator.lower() == "or"
            else Q.AND
            if operator.lower() == "and"
            else Q.XOR
        )
        course_title = request.query_params.get("course_title")
        group_course_number = request.query_params.get("group_course_number")
        semester = request.query_params.get("semester")
        q_obj = Q()
        q_obj.add(Q(course_title__title=course_title), q_operator) if course_title else None
        q_obj.add(Q(group_course_number=group_course_number), q_operator) if group_course_number else None
        q_obj.add(Q(semester=semester), q_operator) if semester else None
        courses = Course.objects.filter(q_obj)
        return Response(
            CourseSerializer(courses, many=True).data, status=status.HTTP_200_OK
        )


class CourseSearchDetailAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        content = CourseDetailSerializer(course, context={"course_id":course_id, 'is_student':hasattr(request.user, 'student_user'), "user_id":request.user.id}).data
        return Response(content, status=status.HTTP_200_OK)
