from open_schools_platform.common.filters import SoftCondition
from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.parent_management.families.services import add_student_profile_to_family, create_family
from open_schools_platform.student_management.students.services import create_student_profile


def get_datadict_list_sorted_by_pk(datadict_list: list):
    return list(sorted(datadict_list, key=lambda x: x["id"]))


def create_student_profile_in_family(i, family):
    studentprofile_creation_data = {
        "name": f"test_student_profile{i + 1}",
        "age": 15 + i,
    }
    student_profile = create_student_profile(**studentprofile_creation_data)
    add_student_profile_to_family(family, student_profile)
    return student_profile


def create_test_family(i, parent):
    return create_family(parent=parent, name=f"test_family{i}")


def get_deleted_families():
    families = get_families(filters={'DELETED': SoftCondition.DELETED_ONLY})
    return families
