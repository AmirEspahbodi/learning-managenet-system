from django.contrib import admin

from .models import (
    Assignment,
    MemberTakeAssignment,
    FTQuestion,
    MemberAssignmentFTQuestion,
)

# Register your models here.


class MemberTakeAssignmentInline(admin.TabularInline):
    model = MemberTakeAssignment
    can_delete = False
    readonly_fields = (
        "assignment",
        "member",
        "last_visit",
        "finish_at",
        "score",
    )


class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = (
        "assignment",
        "title",
        "text",
        "file",
        "statrt_at",
        "end_at",
    )


@admin.register(Assignment)
class PracticeAdmin(admin.ModelAdmin):
    inlines = [FTQuestionInline, MemberTakeAssignmentInline]
    raw_id_fields = ("session",)
    ordering = ("statrt_at", "end_at")
    list_filter = (
        "session__course__course_title__title",
        "session__course",
        "end_at",
    )
    list_display = (
        "session",
        "assignment_number",
        "title",
        "statrt_at",
        "end_at",
    )


class MemberAssignmentFTQuestionInline(admin.TabularInline):
    model = MemberAssignmentFTQuestion
    can_delete = False
    readonly_fields = (
        "member_take_assignment",
        "ft_question",
        "answered_text",
        "answered_file",
    )


@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [MemberAssignmentFTQuestionInline]
    raw_id_fields = ("assignment",)
    ordering = ("statrt_at", "end_at")
    list_filter = ("assignment__session__course", "statrt_at", "end_at")
    list_display = ("assignment", "title", "text", "statrt_at", "end_at")
