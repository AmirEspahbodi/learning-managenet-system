from django.contrib import admin


from .models import Student, StudentEnroll
# Register your models here.


class StudentEnrollInlines(admin.TabularInline):
    model = StudentEnroll
    readonly_fields = ('is_student_paid_percentage', )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = [StudentEnrollInlines]
    raw_id_fields = ('user',)
    list_display = ('user', 'school', 'degree', 'field')
    list_filter = ('school', 'degree', 'field', )
    ordering = ('-user', )


@admin.register(StudentEnroll)
class StudentEnrollAdmin(admin.ModelAdmin):
    raw_id_fields = ('student', 'course')
    readonly_fields = ('is_student_paid_percentage', )
