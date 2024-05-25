from django.db import models

from utils import TimeStampMixin


# Create your models here.
class Permission(TimeStampMixin, models.Model):
    name = models.CharField(max_length=255)
    table = models.CharField(max_length=255)
    operation = models.CharField(max_length=255)
    description = models.TextField()
    sort = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        db_table = "permissions"


class Role(TimeStampMixin, models.Model):
    name = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        db_table = "roles"


class RolePermission(models.Model):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_permissions"
