from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from courses.models import MemberShip, MemberShipRoles, Course
from courses.permissions import IsStudent


class StudentCourseEnrole(GenericAPIView):
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        try:
            course = Course.objects.get(id=kwargs.get('course_id'))
        except ObjectDoesNotExist:
            return Response({'message': 'course does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj = MemberShip.objects.get(
                Q(course=kwargs.get('course_id')) & Q(user=request.user))
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
            print(e)
            return Response(data={"message":"do not try again!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)