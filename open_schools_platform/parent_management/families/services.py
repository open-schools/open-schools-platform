from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile


def add_parent_profile_to_family(family: Family, parent: ParentProfile):
    family.parent_profiles.add(parent)
    family.save()
    return family


def add_student_profile_to_family(family: Family, student_profile: StudentProfile):
    family.student_profiles.add(student_profile)
    family.save()
    return family


def create_family(parent: ParentProfile, name: str = None) -> Family:
    if name is None:
        name = "Family of " + parent.name
    family = Family.objects.create_family(
        name=name,
    )
    add_parent_profile_to_family(family=family, parent=parent)
    return family
