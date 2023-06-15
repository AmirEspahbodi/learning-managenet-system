from django.core.exceptions import ObjectDoesNotExist
from accounts.apis.permissions import IsEmailVerified
from ..models import StudentEnroll


class IsStudent(IsEmailVerified):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.is_student():
                return True
        return False


class IsRelativeStudentMixin:
    def isRelativeStudent(self, request, course):
        student = request.user.student_user
        try:
            studentCourseEnroll = StudentEnroll.objects.get(
                student=student, course=course)
        except ObjectDoesNotExist:
            return False

        if studentCourseEnroll.student == student:
            return True
        return False
