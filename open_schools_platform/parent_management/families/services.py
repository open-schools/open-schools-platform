from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.student.models import StudentProfile


def create_family(name: str) -> Family:
    family = Family.objects.create_family(
        name=name,
    )
    return family


def add_parent_to_family(family: Family, parent: ParentProfile):
    family.parent_profiles.add(parent)
    family.save()
    return family


def add_student_profile_to_family(student_profile: StudentProfile, family: Family):
    family.student_profiles.add(student_profile)
    family.save()
    return family


def generate_name_for_family(parent: ParentProfile) -> str:
    name_for_family = "Family of " + parent.name
    return name_for_family
