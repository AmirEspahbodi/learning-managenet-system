from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from accounts.apis.permissions import IsEmailVerified
from courses.models import Course, MemberShip, MemberShipRoles, Session
from assignments.models import Assignment
from exams.models import Exam


class IsStudent(IsEmailVerified):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.is_student():
                return True
        return False


class IsTeacher(IsEmailVerified):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.is_teacher():
                return True
        return False


class IsRelativeBaseMixin:
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


class IsRelativeStudentMixin(IsRelativeBaseMixin):
    def check_permissions(self, request,  *args, **kwargs):
        '''
        check teacher is relative to this course 
        add course object to self
        '''
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        if not request.user.is_student():
            raise exceptions.PermissionDenied()

        course_id = kwargs.get("course_id")
        try:
            self.course = Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()

        try:
            self.member = MemberShip.objects.get(
                user=request.user, course=self.course, role=MemberShipRoles.STUDENT)
        except ObjectDoesNotExist:
            raise exceptions.PermissionDenied()


class IsRelativeTeacherMixin(IsRelativeBaseMixin):
    def check_permissions(self, request,  *args, **kwargs):
        '''
        check teacher is relative to this course 
        add course object to self
        '''
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        if request.user.is_teacher():
            self.student = request.user.teacher_user
        else:
            raise exceptions.PermissionDenied()

        if "course_id" in kwargs:
            self.course_id = kwargs.get("course_id")
            self.course = Course.objects.get(id=self.course_id)
        elif "session_id" in kwargs:
            self.session_id = kwargs.get("session_id")
            self.session = Session.objects.select_related('course').get(id=self.session_id)
            self.course = self.session.course
        elif 'assignment_id' in kwargs:
            self.assignment_id = self.assignment_id = kwargs.get("assignment_id")
            self.assignment = Assignment.objects.select_related('session').select_related('session__course').get(id=self.assignment_id)
            self.course = self.assignment.session.course
            
        elif 'exam_id' in kwargs:
            self.exam_id = kwargs.get("exam_id")
            self.exam = Exam.objects.select_related('session').select_related('session__course').get(id=self.exam_id)
            self.course = self.exam.session.course

        try:
            self.member = MemberShip.objects.get(
                user=request.user, course=self.course, role=MemberShipRoles.TEACHER)
        except ObjectDoesNotExist:
            raise exceptions.PermissionDenied()
