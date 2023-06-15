from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from accounts.apis.permissions import IsEmailVerified
from ..models import StudentEnroll, Course


class IsStudent(IsEmailVerified):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.is_student():
                return True
        return False


class IsRelativeStudentMixin:
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_permissions(request, *args, **kwargs)
        self.check_throttles(request)

    def check_permissions(self, request,  *args, **kwargs):
        '''
        check teacher is relative to this course 
        add course object to self
        '''
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        if request.user.is_student():
            self.student = request.user.student_user
        else:
            raise exceptions.PermissionDenied()

        course_id = kwargs.get("course_id")
        try:
            self.course = Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()

        try:
            self.studentCourseEnroll = StudentEnroll.objects.get(
                student=self.student, course=self.course)
        except ObjectDoesNotExist:
            raise exceptions.PermissionDenied()
