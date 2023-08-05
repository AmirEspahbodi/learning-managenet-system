from django.contrib import admin

from .models import Teacher, TeacherPublished, TeacherEducation
from courses.models import Course
# Register your models here.


class TeacherPublishedInline(admin.TabularInline):
    model = TeacherPublished
    extra = 1


class TeacherEducationInline(admin.TabularInline):
    model = TeacherEducation
    extra = 1


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inlines = [
        TeacherEducationInline,
        TeacherPublishedInline,
    ]
    ordering = ('-user', )
    list_display = ('user', 'experience')
    list_filter = ('experience', )
    raw_id_fields = ('user',)
