from django.contrib import admin

from .models import Exam, EnrolledStudenTakeExam, FTQuestion, EnrolledStudenExamFTQuestion
# Register your models here.

class EnrolledStudenTakeExamInline(admin.TabularInline):
    model = EnrolledStudenTakeExam
    can_delete = False
    readonly_fields = ('exam', 'student_enroll', 'visit_datetime', 'finish_datetime', 'score')


class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = ('exam', 'title', 'description', 'file', 'start_datetime', 'end_datetime')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [
        FTQuestionInline, EnrolledStudenTakeExamInline
    ]
    raw_id_fields = ('session', )
    ordering = ('create_datetime', 'start_datetime', 'end_datetime')
    list_filter = ('session__course__course_title__title', 'session__course', 'create_datetime', 'start_datetime', 'end_datetime')
    list_display = ('session', 'exam_number', 'title', 'create_datetime', 'start_datetime', 'end_datetime')


class EnrolledStudenExamFTQuestionInline(admin.TabularInline):
    model = EnrolledStudenExamFTQuestion
    can_delete = False
    readonly_fields = ('enrolled_students_take_exam', 'ft_question', 'send_datetime', 'finish_datetime', 'answered_text', 'answered_file')
   

@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [
        EnrolledStudenExamFTQuestionInline
    ]
    raw_id_fields = ('exam',)
    ordering = ('start_datetime', 'end_datetime')
    list_filter = ('exam__session__course', 'start_datetime', 'end_datetime')
    list_display = ('exam', 'title', 'description', 'start_datetime', 'end_datetime')
