from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CourseTitle, Course, CourseTime, Session, MemberShip
from exams.models import Exam
from assignments.models import Assignment

# Register your models here.


# INLINES
class CourseInline(admin.TabularInline):
    ordering = ("start_date",)
    model = Course
    extra = 1


class MemberShipInline(admin.TabularInline):
    ordering = ("-role",)
    model = MemberShip
    extra = 5


class CourseTimeInline(admin.TabularInline):
    ordering = ("-time_slot__day", "-time_slot__start")
    model = CourseTime
    extra = 2


class SessionInline(admin.TabularInline):
    ordering = ("date", "-time_slot__start")
    model = Session
    extra = 2


@admin.register(CourseTitle)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseInline]
    list_display = ("id", "title")


@admin.register(Course)
class GroupCourseAdmin(admin.ModelAdmin):
    raw_id_fields = ("course_title", "semester")
    inlines = [
        MemberShipInline,
        CourseTimeInline,
        SessionInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "course_title",
                    "course_number",
                    "semester",
                ),
            },
        ),
        (
            _("time"),
            {
                "fields": ("start_date", "end_date"),
            },
        ),
        (
            _("tuition"),
            {
                "fields": (
                    "tuition",
                    "tuition_percentage",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "course_title",
                    "course_number",
                    "semester",
                    "tuition",
                    "tuition_percentage",
                )
            },
        ),
    )
    list_display = ("course_title", "course_number", "semester")
    list_filter = ("course_title__title", "semester__semester_id")


@admin.register(CourseTime)
class GroupCourseTimesAdmin(admin.ModelAdmin):
    list_display = ("course", "semester", "time_slot")


class SessionAssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1


class SessionExamsInline(admin.TabularInline):
    model = Exam
    extra = 1


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    inlines = [SessionAssignmentInline, SessionExamsInline]
    ordering = (
        "-date",
        "-time_slot__start",
    )


admin.site.register(MemberShip)
