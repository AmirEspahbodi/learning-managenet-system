from django.contrib import admin


from .models import Student, StudentTakes
# Register your models here.


class StudentTakesInlines(admin.TabularInline):
    model = StudentTakes
    readonly_fields = ('is_student_paid_percentage', )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = [StudentTakesInlines]
    raw_id_fields = ('user',)
    list_display = ( 'user', 'school', 'degree', 'field')
    list_filter = ('school', 'degree', 'field', )
    ordering = ('-user', )


@admin.register(StudentTakes)
class StudentTakesAdmin(admin.ModelAdmin):
    raw_id_fields = ('student', 'group_course')
    readonly_fields = ('is_student_paid_percentage', )
