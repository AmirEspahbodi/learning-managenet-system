import uuid
from datetime import datetime
from django.db import models

from jalali_date import datetime2jalali

from courses.models import Session, MemberShip
from core.db.mixins.timestamp import TimeStampMixin

# Create your models here.


class Content(TimeStampMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="contents"
    )
    content_number = models.PositiveSmallIntegerField(
        null=True, blank=True, editable=False
    )
    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="contents/teachers")
    accessing_at = models.DateTimeField(
        auto_now_add=True, help_text="default is current time"
    )

    def __str__(self):
        return "content : " + str(self.session.course) + " " + str(self.content_number)


class MemberVisitContent(TimeStampMixin):
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name="member_contents"
    )
    member = models.ForeignKey(MemberShip, on_delete=models.CASCADE)
    last_visit = models.DateTimeField(auto_now_add=True)

    def get_jalali_visit_datetime(self):
        return str(datetime2jalali(self.last_visit))

    def __str__(self):
        return (
            str(self.content)
            + " "
            + str(self.member.user)
            + " "
            + str(datetime2jalali(self.last_visit))
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content", "member"],
                name="unique_member_content",
            )
        ]
