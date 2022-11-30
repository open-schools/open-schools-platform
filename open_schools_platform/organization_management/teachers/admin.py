from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from open_schools_platform.common.admin import InputFilter, BaseAdmin, admin_wrapper
from open_schools_platform.student_management.students.admin import CircleFilter
from open_schools_platform.organization_management.teachers.models import TeacherProfile, Teacher
from open_schools_platform.organization_management.teachers.selectors import get_teachers


class TeacherProfileFilter(InputFilter):
    parameter_name = 'teacher_profile_name'
    title = _('teacher profile name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            teacher_profile = self.value()

            return get_teachers(filters={'teacher_profile_name': teacher_profile})


@admin_wrapper
class TeacherProfileAdmin(BaseAdmin):
    list_display = ('name', 'age', 'user', 'id', 'phone', 'photo')
    search_fields = ('name', 'age', 'user__phone', 'phone')


@admin_wrapper
class TeacherAdmin(BaseAdmin):
    list_display = ('teacher_profile', 'circle', 'id')
    search_fields = ("name",)
    list_filter = (CircleFilter, TeacherProfileFilter)


admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(Teacher, TeacherAdmin)
