from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter

from open_schools_platform.common.admin import InputFilter
from open_schools_platform.common.models import DeleteAdmin
from open_schools_platform.student_management.students.models import StudentProfile, Student
from django.utils.translation import gettext_lazy as _

from open_schools_platform.student_management.students.selectors import get_students


class CircleFilter(InputFilter):
    parameter_name = 'circle_name'
    title = _('circle name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            circle = self.value()

            return get_students(filters={'circle_name': circle})


class StudentProfileFilter(InputFilter):
    parameter_name = 'student_profile_name'
    title = _('student profile name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            student_profile = self.value()

            return get_students(filters={'student_profile_name': student_profile})


class StudentProfileAdmin(DeleteAdmin):
    list_display = DeleteAdmin.list_display + ('age', 'user', 'id', 'phone')
    search_fields = ('name', 'age', "user__phone", 'phone')
    list_filter = DeleteAdmin.list_filter


DeleteAdmin.init_model(StudentProfileAdmin)


class StudentAdmin(DeleteAdmin):
    list_display = DeleteAdmin.list_display + ('student_profile', 'circle', 'id')
    search_fields = ("name",)
    list_filter = DeleteAdmin.list_filter + (CircleFilter, StudentProfileFilter, StudentProfileFilter)


DeleteAdmin.init_model(StudentAdmin)


admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Student, StudentAdmin)
