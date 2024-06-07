from django.db import models
from django.utils.translation import gettext_lazy as _

from utils import TimeStampMixin
from accounts.models import User


class RoleCreationPrivilegeStatus(models.IntegerChoices):
    DIRECTLY_BY_PRIVILEGED_ADMINS = 1, _(
        "These roles are created directly by privileged admins."
    )
    NEED_VERIFICATION = 2, _(
        "The user who selected this role needs to submit their complete information for validation."
    )
    OPEN = 3, _("Users can choose this role freely.")


class Permission(TimeStampMixin):
    name = models.CharField(max_length=255)
    table = models.CharField(max_length=255)
    operation = models.CharField(max_length=255)
    description = models.TextField()
    sort = models.PositiveIntegerField()

    def __str__(self):
        return f"Permission(name={self.name})"

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "permissions"


class Role(TimeStampMixin):
    name = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    creation_privilege = models.PositiveIntegerField(
        choices=RoleCreationPrivilegeStatus.choices,
        default=RoleCreationPrivilegeStatus.OPEN,
    )

    def __str__(self):
        return f"Permission(name={self.name})"

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "roles"


class AdminPrivilege(TimeStampMixin):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField()
    sort = models.PositiveIntegerField()

    def __str__(self):
        return f"AdminPrivilege(name={self.name})"

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "admin_privileges"


class RoleAdminPrivilege(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    admin_privilege = models.ForeignKey(AdminPrivilege, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_admin_privileges"


class RolePermission(models.Model):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"RolePermission(role={self.role.name}, permission={self.permission.name})"
        )

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "role_permissions"


class UserRole(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"UserRole(user={self.user.username}, role={self.role.name})"

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "user_roles"


class UserRolePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, null=True, blank=True
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserRolePermission(user={self.user.username}, role={self.user_role.role.name}, permission={self.permission.name})"

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = "user_role_permissions"
