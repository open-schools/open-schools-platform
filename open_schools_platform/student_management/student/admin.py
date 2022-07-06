from django.contrib import admin
from open_schools_platform.student_management.student.models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'age')
