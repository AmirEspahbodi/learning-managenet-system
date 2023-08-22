from django.db import models
from courses.models import Session, MemberShip
from jalali_date import datetime2jalali
from core.db.mixins.timestamp import TimeStampMixin

# Create your models here.


class Assignment(TimeStampMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    assignment_number = models.PositiveSmallIntegerField(
        null=True, blank=True, editable=False
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def get_jalali_created_at(self):
        return str(datetime2jalali(self.created_at))[:19]

    def get_jalali_start_at(self):
        return str(datetime2jalali(self.start_at))[:19]

    def get_jalali_end_at(self):
        return str(datetime2jalali(self.end_at))[:19]

    def __str__(self):
        return f"assignment : {self.session.course} {self.assignment_number}"

    class Meta:
        db_table_comment = "assignment for each session of course"


class MemberTakeAssignment(TimeStampMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="assignment_members"
    )
    member = models.ForeignKey(
        MemberShip,
        on_delete=models.CASCADE,
    )
    last_visit = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(auto_now=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"student assignment: {self.assignment} {self.member.user} {datetime2jalali(self.finish_at)}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "member"],
                name="unique_assignments_member_take_assignment",
            )
        ]
        db_table = "assignments_member_take_assignment"
        db_table_comment = "a table betwen student takes and assignment. It shows that the student participated in the assignment"


class FTQuestion(TimeStampMixin):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="ftquestions"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="assignment/questions/", null=True, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    class Meta:
        db_table = "assignments_ftquestion"
        db_table_comment = "Each assignment can have several file/text type questions. This table stores questions of this type for each assignment"

    def __str__(self):
        return f"f/t question:  {self.assignment} {self.title[:50]}"


class FTQuestionAnswer(TimeStampMixin):
    ft_question = models.ForeignKey(
        FTQuestion, on_delete=models.CASCADE, related_name="ftquestion_answers"
    )
    answer_text = models.TextField(null=True, blank=True)
    answer_file = models.FileField(
        upload_to="assignment/teacher/answers/", null=True, blank=True
    )
    accessing_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "assignments_ftquestion_answer"
        db_table_comment = "answer of the file/text type questions"


class MemberAssignmentFTQuestion(TimeStampMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )
    member_take_assignment = models.ForeignKey(
        MemberTakeAssignment,
        on_delete=models.CASCADE,
        related_name="member_take_assignment_ftquestions",
    )
    ft_question = models.ForeignKey(FTQuestion, on_delete=models.CASCADE)
    answered_text = models.TextField(null=True, blank=True)
    answered_file = models.FileField(
        upload_to="assignment/students/answers/", null=True, blank=True
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member_take_assignment", "ft_question"],
                name="unique_member_assignment_studen_assignment_fttquestion",
            )
        ]
        db_table = "assignments_member_assignment_fttquestion"
        db_table_comment = "This table stores the student's answer to the assignment file/text question"

    def __str__(self):
        return f"student assignment question answer: {self.member_take_assignment.assignment} {self.ft_question.title} {datetime2jalali(self.finish_at)}"
