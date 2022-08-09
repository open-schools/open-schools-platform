from django.contrib import admin
from django.db.models import Q

from open_schools_platform.common.admin import InputFilter
from open_schools_platform.student_management.students.models import StudentProfile, Student
from django.utils.translation import gettext_lazy as _


class CircleFilter(InputFilter):
    parameter_name = 'circle'
    title = _('circle')

    def queryset(self, request, queryset):
        if self.value() is not None:
            circle = self.value()

            return queryset.filter(
                Q(circle__name__icontains=circle)
            )


class StudentProfileFilter(InputFilter):
    parameter_name = 'student_profile'
    title = _('student profile')

    def queryset(self, request, queryset):
        if self.value() is not None:
            student_profile = self.value()

            return queryset.filter(
                Q(student_profile__name__icontains=student_profile)
            )


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'user', 'id')
    search_fields = ('name', 'age', "user__phone")


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_profile', 'circle', 'id')
    search_fields = ("name",)
    list_filter = (CircleFilter, StudentProfileFilter)


admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Student, StudentAdmin)
