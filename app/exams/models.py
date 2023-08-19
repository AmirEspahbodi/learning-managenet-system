import uuid
from django.db import models
from courses.models import Session, MemberShip
from jalali_date import datetime2jalali
from core.db.mixins.timestamp import TimeStampMixin

# Create your models here.


class Exam(TimeStampMixin):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam_number = models.PositiveSmallIntegerField(editable=False)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def get_jalali_created_at(self):
        return str(datetime2jalali(self.created_at))[:19]

    def get_jalali_start_at(self):
        return str(datetime2jalali(self.start_at))[:19]

    def get_jalali_end_at(self):
        return str(datetime2jalali(self.end_at))[:19]

    def __str__(self):
        return f"exam : {self.session.course} {self.exam_number}"

    class Meta:
        db_table_comment = "exam for each session of course"


class MemberTakeExam(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="exam_members"
    )
    member = models.ForeignKey(
        MemberShip,
        on_delete=models.CASCADE,
    )
    last_visit = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"student exam: {self.exam} {self.memeber.user} {datetime2jalali(self.finish_at)}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "member"], name="unique_exams_member_take_exam"
            )
        ]
        db_table = "exams_member_take_exam"
        db_table_comment = "a table betwen student takes and exam. It shows that the student participated in the exam"


class FTQuestion(TimeStampMixin):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="ftquestions")
    title = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="exam/questions/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    class Meta:
        db_table = "exams_ftquestion"
        db_table_comment = "Each exam can have several file/text type questions. This table stores questions of this type for each exam"

    def __str__(self):
        return f"f/t question:  {self.exam} {self.title[:50]}"


class FTQuestionAnswer(TimeStampMixin):
    ft_question = models.ForeignKey(
        FTQuestion, on_delete=models.CASCADE, related_name="ftquestion_answers"
    )
    answer_text = models.TextField(null=True, blank=True)
    answer_file = models.FileField(
        null=True, blank=True, upload_to="exam/teacher/answers/"
    )

    class Meta:
        db_table = "exams_ftquestion_answer"
        db_table_comment = "answer of the file/text type questions"


class MemberExamFTQuestion(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_take_exam = models.ForeignKey(
        MemberTakeExam,
        on_delete=models.CASCADE,
        related_name="member_take_exam_ftquestions",
    )
    ft_question = models.ForeignKey(FTQuestion, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    answered_text = models.TextField(null=True, blank=True)
    answered_file = models.FileField(
        upload_to="exam/students/answers/", null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member_take_exam", "ft_question"],
                name="unique_exams_member_exam_ftquestion",
            )
        ]
        db_table = "exams_member_exam_ftquestion"
        db_table_comment = (
            "This table stores the student's answer to the exam file/text question"
        )

    def __str__(self):
        return f"student exam question answer: {self.member_take_exam.exam} {self.ft_question.title} {datetime2jalali(self.finish_at)}"
