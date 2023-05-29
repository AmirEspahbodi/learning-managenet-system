from django.contrib import admin

from .models import Assignment, EnrolledStudenTakeAssignment, FTQuestion, EnrolledStudenAssignmentFTQuestion
# Register your models here.

class EnrolledStudenTakeAssignmentInline(admin.TabularInline):
    model = EnrolledStudenTakeAssignment
    can_delete = False
    readonly_fields = ('assignment', 'student_enroll', 'visit_datetime', 'finish_datetime', 'score')
    
class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = ('assignment', 'title', 'description', 'file', 'start_datetime', 'end_datetime')


@admin.register(Assignment)
class PracticeAdmin(admin.ModelAdmin):
    inlines = [
        FTQuestionInline, EnrolledStudenTakeAssignmentInline
    ]
    raw_id_fields = ('session', )
    ordering = ('create_datetime', 'start_datetime', 'end_datetime')
    list_filter = ('session__course__course_title__title', 'session__course', 'create_datetime', 'start_datetime', 'end_datetime')
    list_display = ('session', 'assignment_number', 'title', 'create_datetime', 'start_datetime', 'end_datetime')


class EnrolledStudenAssignmentFTQuestionInline(admin.TabularInline):
    model = EnrolledStudenAssignmentFTQuestion
    can_delete = False
    readonly_fields = ('enrolled_students_take_assignment', 'ft_question', 'send_datetime', 'finish_datetime', 'answered_text', 'answered_file')
   

@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [
        EnrolledStudenAssignmentFTQuestionInline
    ]
    raw_id_fields = ('assignment',)
    ordering = ('start_datetime', 'end_datetime')
    list_filter = ('assignment__session__course', 'start_datetime', 'end_datetime')
    list_display = ('assignment', 'title', 'description', 'start_datetime', 'end_datetime')
