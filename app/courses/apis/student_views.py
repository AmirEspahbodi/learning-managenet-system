from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from courses.permissions import IsStudent
from courses.models import Course
from students.models import FinancialAids
from students.apis.serializers import StudentFinancialAidsSerializer

class FinancialAidsAPIView(GenericAPIView):
    serializer_class = StudentFinancialAidsSerializer
    permission_classes = [IsStudent]
    def post(self, request, *args, **kwargs):
        student = request.user.student_user
        try:
            course = Course.objects.get(id=kwargs.get('course_id'))
        except ObjectDoesNotExist as e:
            return Response(data={'detail': "course does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        financial_aid_exist = FinancialAids.objects.filter(
            Q(student=student) & Q(course=course)
        ).exists()
        if financial_aid_exist:
            return Response(data={'detail': 'financial aid already axist!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            financial_aid = serializer.save(student=student, course=course)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)