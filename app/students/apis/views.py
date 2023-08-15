from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course, MemberShip, MemberShipRoles
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsStudent, IsRelativeStudentMixin
from students.models import FinancialAids
from students.apis.serializers import StudentFinancialAids

class StudentHomeAPIView(GenericAPIView):
    permission_classes = [IsStudent]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        now = timezone.now().date()
        day_next_week = (timezone.now() + timedelta(days=7)).date()
        st_memberships = MemberShip.objects.filter(
            user=request.user, role=MemberShipRoles.STUDENT).select_related('course')
        courses = [
            st_membership.course for st_membership in st_memberships]
        week_sessions = Session.objects.filter(Q(date__gte=now) & 
                                               Q(date__lte=day_next_week) & Q(course__in=courses))
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

class StudentCourseEnroleAPIView(GenericAPIView):
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        try:
            course = Course.objects.get(id=kwargs.get('course_id'))
        except ObjectDoesNotExist:
            return Response({'message': 'course does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = MemberShip.objects.get(
                Q(course=kwargs.get('course_id')) & Q(user=request.user))
            if obj is not None:
                return Response({'message': 'you are already enrolled'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass
        try:
            MemberShip.objects.create(
                user=request.user,
                role=MemberShipRoles.STUDENT,
                course=course
            )
        except BaseException as e:
            return Response(data={"message":"do not try again!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)


class StudentGetFinancialAidAPIView(GenericAPIView):
    permission_classes = [IsStudent]
    def get(self, request, *args, **kwargs):
        financial_aids = request.user.student_user.financial_aids
        return Response(data=StudentFinancialAids(financial_aids, many=True).data, status=status.HTTP_200_OK)
