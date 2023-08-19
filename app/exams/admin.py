from django.contrib import admin

from .models import Exam, MemberTakeExam, FTQuestion, MemberExamFTQuestion

# Register your models here.


class MemberTakeExamInline(admin.TabularInline):
    model = MemberTakeExam
    can_delete = False
    readonly_fields = ("exam", "member", "last_visit", "finish_at", "score")


class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = (
        "exam",
        "title",
        "text",
        "file",
        "start_at",
        "end_at",
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [FTQuestionInline, MemberTakeExamInline]
    raw_id_fields = ("session",)
    ordering = ("start_at", "end_at")
    list_filter = (
        "session__course__course_title__title",
        "session__course",
        "start_at",
        "end_at",
    )
    list_display = (
        "session",
        "exam_number",
        "title",
        "start_at",
        "end_at",
    )


class MemberExamFTQuestionInline(admin.TabularInline):
    model = MemberExamFTQuestion
    can_delete = False
    readonly_fields = (
        "member_take_exam",
        "ft_question",
        "updated_at",
        "answered_text",
        "answered_file",
    )


@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [MemberExamFTQuestionInline]
    raw_id_fields = ("exam",)
    ordering = ("start_at", "end_at")
    list_filter = ("exam__session__course", "start_at", "end_at")
    list_display = ("exam", "title", "text", "start_at", "end_at")
