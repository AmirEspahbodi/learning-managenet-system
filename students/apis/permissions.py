from accounts.apis.permissions import IsEmailVerified

class IsStudent(IsEmailVerified):
    def has_permission(self, request, view):
        if super(IsStudent, self).has_permission():
            if hasattr(request, 'student'):
                return True
        return False
