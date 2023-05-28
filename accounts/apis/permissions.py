from rest_framework.permissions import BasePermission

class IsEmailVerified(BasePermission):
    def has_permission(self, request, view):
        if  request.user and request.user.is_authenticated:
            return request.user.is_email_verified()
        return False

class IsEmailAndPhoneVerified(BasePermission):
    def has_permission(self, request, view):
        if  request.user and request.user.is_authenticated:
            return request.user.is_email_verified() and request.user.is_phone_number_verified()
        return False

class IsEmailOrPhoneVerified(BasePermission):
    def has_permission(self, request, view):
        if  request.user and request.user.is_authenticated:
            return request.user.is_email_verified() or request.user.is_phone_number_verified()
        return False
