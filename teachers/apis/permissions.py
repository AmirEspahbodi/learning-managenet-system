from accounts.apis.permissions import IsEmailVerified
from courses.models import Course


class IsTeacher(IsEmailVerified):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.is_student():
                return True
        return False


class IsRelativeTeacherMixin:
    def isRelativeTeacer(self, request, course):
        teacher = request.user.teacher_user
        if course.teacher == teacher:
            return True
        return False
