from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import StackedInline
from .forms import UserCreationForm, UserChangeForm
from .models import UserInformation, PasswordResetCode, EmailVerificationCode
# Register your models here.

User = get_user_model()


class UserInfoAdminInline(StackedInline):
    model = UserInformation


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [UserInfoAdminInline]
    add_form = UserCreationForm
    form = UserChangeForm
    list_filter = ("role", "is_superuser", "is_active", "groups")
    list_display = ("username", "email", "phone_number",
                    "role", "first_name", "last_name")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email",  "phone_number", "role", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {
         "fields": ("first_name", "last_name", "email", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "role",
                    "verification_status",
                    "groups",
                    "user_permissions"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )


@admin.register(PasswordResetCode)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'ip_address', 'user_agent')


@admin.register(EmailVerificationCode)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'ip_address', 'user_agent')
