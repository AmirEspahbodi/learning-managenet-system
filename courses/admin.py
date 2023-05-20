from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from .models import CourseTitle, Course, GroupCourseTimes, Session


##INLINES
class CourseInline(admin.TabularInline):
    model = Course
    extra = 1


class GroupCourseTimesInline(admin.TabularInline):
    model = GroupCourseTimes
    extra = 2

 
class SessionInline(admin.TabularInline):
    model = Session
    extra = 2
    ordering = ('date','time_slot__start')


@admin.register(CourseTitle)
class CourseAdmin(admin.ModelAdmin):
    inlines = [
        CourseInline
    ]
    list_display = ('id', 'title')


@admin.register(Course)
class GroupCourseAdmin(admin.ModelAdmin):
    raw_id_fields = ("course_title",'semester', 'teacher')
    inlines = [
        GroupCourseTimesInline,
        SessionInline,
    ]
    fieldsets = (
        (None, {
                'fields': ('group_course_number', 'course_title', 'semester', 'teacher', ),
            }
        ),
        (_('time'), {
                'fields':('start_date', 'end_date'),
            }
        ),
        (_('tuition'), {
                'fields':('tuition', 'percentage_required_for_tuition',),
            }
        )
    )
    add_fieldsets = (
        (None, {'fields': ('group_course_number', 'semester', 'teacher', 'tuition', 'percentage_required_for_tuition')}),
    )
    
    list_display = ('group_course_number', 'semester', 'teacher')
    
    list_filter = ('course_title__title', 'semester__semester_id', 'teacher__user')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    ordering = ('-date', '-time_slot__start',)


@admin.register(GroupCourseTimes)
class GroupCourseTimesAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'time_slot')
