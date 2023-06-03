from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from accounts.models import Roles

def get_student(request):
    return request.user.student_user

def get_teacher(request):
    return request.user.teacher_user


class RoleDetermination(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if request.user.role == Roles.STUDENT:
                request.student = SimpleLazyObject(lambda: get_student(request))
            elif request.user.role == Roles.TEACHER:
                request.teacher = SimpleLazyObject(lambda: get_teacher(request))
