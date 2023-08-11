import uuid
from django.db import models
from courses.models import Session, MemberShip
from jalali_date import datetime2jalali

# Create your models here.


class Assignment(models.Model):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    assignment_number = models.PositiveSmallIntegerField(
        null=True, blank=True, editable=False)
    create_datetime = models.DateTimeField(auto_now_add=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def get_jalali_create_datetime(self):
        return str(datetime2jalali(self.create_datetime))[:19]

    def get_jalali_start_datetime(self):
        return str(datetime2jalali(self.start_datetime))[:19]

    def get_jalali_end_datetime(self):
        return str(datetime2jalali(self.end_datetime))[:19]

    def __str__(self):
        return f"assignment : {self.session.course} {self.assignment_number}"

    class Meta:
        db_table_comment = "assignment for each session of course"


class MemberTakeAssignment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='members_assignment'
    )
    member = models.ForeignKey(
        MemberShip,
        on_delete=models.CASCADE,
    )
    visit_datetime = models.DateTimeField(auto_now_add=True)
    finish_datetime = models.DateTimeField(auto_now=True)
    score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"student assignment: {self.assignment} {self.member.user} {datetime2jalali(self.finish_datetime)}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'assignment',
                    'member'
                ],
                name='unique_assignments_member_take_assignment'
            )
        ]
        db_table = "assignments_member_take_assignment"
        db_table_comment = "a table betwen student takes and assignment. It shows that the student participated in the assignment"


class FTQuestion(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(
        upload_to='assignment/questions/', null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        db_table = "assignments_ftquestion"
        db_table_comment = "Each assignment can have several file/text type questions. This table stores questions of this type for each assignment"

    def __str__(self):
        return f"f/t question:  {self.assignment} {self.title[:50]}"


class FTQuestionAnswer(models.Model):
    ft_question = models.ForeignKey(
        FTQuestion,
        on_delete=models.CASCADE
    )
    answer_text = models.TextField(null=True, blank=True)
    answer_file = models.FileField(upload_to='assignment/teacher/answers/')

    class Meta:
        db_table = "assignments_ftquestion_answer"
        db_table_comment = "answer of the file/text type questions"


class MemberAssignmentFTQuestion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    member_take_assignment = models.ForeignKey(
        MemberTakeAssignment,
        on_delete=models.CASCADE,
    )
    ft_question = models.ForeignKey(
        FTQuestion,
        on_delete=models.CASCADE
    )
    send_datetime = models.DateTimeField()
    finish_datetime = models.DateTimeField()
    answered_text = models.TextField(null=True, blank=True)
    answered_file = models.FileField(
        upload_to='assignment/students/answers/', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'member_take_assignment',
                    'ft_question'
                ],
                name='unique_member_assignment_studen_assignment_fttquestion'
            )
        ]
        db_table = "assignments_member_assignment_fttquestion"
        db_table_comment = "This table stores the student's answer to the assignment file/text question"

    def __str__(self):
        return f"student assignment question answer: {self.member_take_assignment.assignment} {self.ft_question.title} {datetime2jalali(self.finish_datetime)}"
