from django.contrib import admin

from .models import Assignment, MemberTakeAssignment, FTQuestion, MemberAssignmentFTQuestion
# Register your models here.


class MemberTakeAssignmentInline(admin.TabularInline):
    model = MemberTakeAssignment
    can_delete = False
    readonly_fields = ('assignment', 'member',
                       'visit_datetime', 'finish_datetime', 'score')


class FTQuestionInline(admin.TabularInline):
    model = FTQuestion
    can_delete = False
    readonly_fields = ('assignment', 'title', 'text', 'file',
                       'start_datetime', 'end_datetime')


@admin.register(Assignment)
class PracticeAdmin(admin.ModelAdmin):
    inlines = [
        FTQuestionInline, MemberTakeAssignmentInline
    ]
    raw_id_fields = ('session', )
    ordering = ('create_datetime', 'start_datetime', 'end_datetime')
    list_filter = ('session__course__course_title__title', 'session__course',
                   'create_datetime', 'start_datetime', 'end_datetime')
    list_display = ('session', 'assignment_number', 'title',
                    'create_datetime', 'start_datetime', 'end_datetime')


class MemberAssignmentFTQuestionInline(admin.TabularInline):
    model = MemberAssignmentFTQuestion
    can_delete = False
    readonly_fields = ('member_take_assignment', 'ft_question',
                       'send_datetime', 'finish_datetime', 'answered_text', 'answered_file')


@admin.register(FTQuestion)
class FTQuestionAdmin(admin.ModelAdmin):
    inlines = [
        MemberAssignmentFTQuestionInline
    ]
    raw_id_fields = ('assignment',)
    ordering = ('start_datetime', 'end_datetime')
    list_filter = ('assignment__session__course',
                   'start_datetime', 'end_datetime')
    list_display = ('assignment', 'title', 'text',
                    'start_datetime', 'end_datetime')
