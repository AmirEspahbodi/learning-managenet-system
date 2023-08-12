from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .serialisers import FinancialAidsResultSerializer
from courses.models import Session, Course, MemberShip, MemberShipRoles
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsTeacher, IsRelativeTeacherMixin
from students.models import Student, FinancialAids
from students.apis.serializers import ShowFinancialAids
from django.contrib.auth import get_user_model

User = get_user_model()

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


class TeacherSessionDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class TeacherFinancialAidsAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ShowFinancialAids
    
    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        financial_aids = FinancialAids.objects.filter(course=course_id)
        return Response(data=ShowFinancialAids(financial_aids, many=True).data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = FinancialAidsResultSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data
        try:
            user = User.objects.get(id=data['user_id'])
        except ObjectDoesNotExist:
            return Response(data={'detail': 'student does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=kwargs.get('course_id'))
        except ObjectDoesNotExist:
            return Response(data={'detail': 'course does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if data["is_accepted"]:
            MemberShip.objects.get_or_create(
                course = course,
                user = user,
                role = MemberShipRoles.STUDENT
            )
        FinancialAids.objects.filter(id=data["financial_id"]).update(
            result = data["result"],
            is_accepted = data["is_accepted"],
        )
        
        return Response(data={"message":"OK"}, status=status.HTTP_200_OK)
