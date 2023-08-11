from django.contrib import admin

from .models import Exam, MemberTakeExam, FTQuestion, MemberExamFTQuestion

# Register your models here.


class MemberTakeExamInline(admin.TabularInline):
    model = MemberTakeExam
    can_delete = False
    readonly_fields = ('exam', 'member',
                       'visit_datetime', 'finish_datetime', 'score')


class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = ('exam', 'title', 'text', 'file',
                       'start_datetime', 'end_datetime')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [
        FTQuestionInline, MemberTakeExamInline
    ]
    raw_id_fields = ('session', )
    ordering = ('create_datetime', 'start_datetime', 'end_datetime')
    list_filter = ('session__course__course_title__title', 'session__course',
                   'create_datetime', 'start_datetime', 'end_datetime')
    list_display = ('session', 'exam_number', 'title',
                    'create_datetime', 'start_datetime', 'end_datetime')


class MemberExamFTQuestionInline(admin.TabularInline):
    model = MemberExamFTQuestion
    can_delete = False
    readonly_fields = ('member_take_exam', 'ft_question',
                       'send_datetime', 'finish_datetime', 'answered_text', 'answered_file')


@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [
        MemberExamFTQuestionInline
    ]
    raw_id_fields = ('exam',)
    ordering = ('start_datetime', 'end_datetime')
    list_filter = ('exam__session__course', 'start_datetime', 'end_datetime')
    list_display = ('exam', 'title', 'text', 'start_datetime', 'end_datetime')
