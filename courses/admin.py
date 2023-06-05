from django.contrib import admin

from .models import CourseTitle, Course, CourseTime, Session

from students.models import StudentEnroll

from exams.models import Exam
from assignments.models import Assignment
# Register your models here.
from django.utils.translation import gettext_lazy as _


# INLINES
class CourseInline(admin.TabularInline):
    model = Course
    extra = 1


class CourseTimeInline(admin.TabularInline):
    model = CourseTime
    extra = 2


class StudentEnrollInline(admin.TabularInline):
    model = StudentEnroll
    readonly_fields = ('is_student_paid_percentage', )
    extra = 5


class SessionInline(admin.TabularInline):
    model = Session
    extra = 2
    ordering = ('date', 'time_slot__start')


@admin.register(CourseTitle)
class CourseAdmin(admin.ModelAdmin):
    inlines = [
        CourseInline
    ]
    list_display = ('id', 'title')


@admin.register(Course)
class GroupCourseAdmin(admin.ModelAdmin):
    raw_id_fields = ("course_title", 'semester', 'teacher')
    inlines = [
        CourseTimeInline,
        SessionInline,
        StudentEnrollInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('course_title', 'group_course_number', 'semester', 'teacher', ),
        }
        ),
        (_('time'), {
            'fields': ('start_date', 'end_date'),
        }
        ),
        (_('tuition'), {
            'fields': ('tuition', 'percentage_required_for_tuition',),
        }
        )
    )
    add_fieldsets = (
        (None, {'fields': ('course_title', 'group_course_number', 'semester',
         'teacher', 'tuition', 'percentage_required_for_tuition')}),
    )

    list_display = ('course_title', 'group_course_number',
                    'semester', 'teacher')

    list_filter = ('course_title__title',
                   'semester__semester_id', 'teacher__user')


@admin.register(CourseTime)
class GroupCourseTimesAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'time_slot')


class SessionAssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1


class SessionExamsInline(admin.TabularInline):
    model = Exam
    extra = 1


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    inlines = [
        SessionAssignmentInline, SessionExamsInline
    ]
    ordering = ('-date', '-time_slot__start',)
