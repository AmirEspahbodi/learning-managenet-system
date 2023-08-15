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
        memberships = MemberShip.objects.filter(
            user=request.user, role=MemberShipRoles.TEACHER).select_related("course")
        courses = [membership.course for membership in memberships]
        week_sessions = Session.objects.filter(Q(date__gte=now) & Q(
            date__lt=day_next_week) & Q(course__in=courses))
        print([week_session.date for week_session in week_sessions])
        return Response({
            'courses': CourseSerializer(courses,  many=True).data,
            'sessions': SessionSerializer(week_sessions, many=True).data,
            "now": now
        },
            status=status.HTTP_200_OK
        )


class TeacherCourseDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = SessionSerializer
    def get(self, request, *args, **kwargs):
        sessions = Session.objects.filter(course=self.course).order_by('date')
        return Response({"sessions": SessionSerializer(sessions, many=True).data}, status=status.HTTP_200_OK)


class TeacherSessionDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = SessionSerializer
    def get(self, request, *args, **kwargs):
        return Response(
            data=SessionSerializer(self.session).data,
            status=status.HTTP_200_OK
        )


class TeacherFinancialAidsAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ShowFinancialAids
    
    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        financial_aids = FinancialAids.objects.filter(course=course_id).select_related('student').select_related('student__user')
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
        FinancialAids.objects.filter(id=data["financial_id"]).update(
            result = data["result"],
            is_accepted = data["is_accepted"],
            reviewed=True,
        )
        if data["is_accepted"]:
            if not (MemberShip.objects.filter(
                Q(course=course), Q(user=user))).exists():
                MemberShip.objects.create(
                    course = course,
                    user = user,
                    role = MemberShipRoles.STUDENT
                )
            else:
                return Response(data={'detail':'student is already member of course'}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response(data={"message":"OK"}, status=status.HTTP_200_OK)
