from django.contrib import admin
from .models import Student
# Register your models here.


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'school', 'degree', 'field')
    list_filter = ('school', 'degree', 'field', )
    ordering = ('-user', )

