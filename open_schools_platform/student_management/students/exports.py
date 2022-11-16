from import_export import resources

from open_schools_platform.student_management.students.models import Student


class StudentExport(resources.ModelResource):
    @staticmethod
    def dehydrate_circle(student):
        return student.circle.name

    class Meta:
        model = Student
        exclude = ('deleted', 'deleted_by_cascade', 'student_profile')
