from django.db import models


class TimeStampMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_delted = models.BooleanField(default=False)
    deleted_at = models.BooleanField(null=True, blank=True)
