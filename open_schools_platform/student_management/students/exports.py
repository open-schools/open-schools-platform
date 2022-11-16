from import_export import resources
from import_export.fields import Field

from open_schools_platform.student_management.students.models import Student


class StudentExport(resources.ModelResource):
    phone = Field()

    @staticmethod
    def dehydrate_circle(student):
        return student.circle.name

    @staticmethod
    def dehydrate_phone(student):
        return student.student_profile and student.student_profile.phone

    class Meta:
        model = Student
        exclude = ('deleted', 'deleted_by_cascade', 'student_profile')
        export_order = ('id', 'name', 'phone', 'circle', 'created_at', 'updated_at')
