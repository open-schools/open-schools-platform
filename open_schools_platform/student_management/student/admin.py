from django.contrib import admin
from open_schools_platform.student_management.student.models import StudentProfile, Student


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'age')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Student, StudentAdmin)
