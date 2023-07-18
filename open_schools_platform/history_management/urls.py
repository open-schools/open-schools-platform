from django.urls import path

from open_schools_platform.history_management.views import UserHistoryApi, OrganizationHistoryApi, EmployeeHistoryApi, \
    CircleHistoryApi, StudentHistoryApi, StudentProfileHistoryApi, EmployeeProfileHistoryApi, ParentProfileHistoryApi, \
    FamilyHistoryApi

urlpatterns = [
    path('/user/<uuid:user_id>', UserHistoryApi.as_view(), name='user-history'),
    path('/organization/<uuid:organization_id>', OrganizationHistoryApi.as_view(), name='organization-history'),
    path('/employee/<uuid:employee_id>', EmployeeHistoryApi.as_view(), name='employee_history'),
    path('/employee-profile/<uuid:employee_profile_id>', EmployeeProfileHistoryApi.as_view(),
         name='employee-profile-history'),
    path('/circle/<uuid:circle_id>', CircleHistoryApi.as_view(), name='circle-history'),
    path('/student/<uuid:student_id>', StudentHistoryApi.as_view(), name='student-history'),
    path('/student-profile/<uuid:student_profile_id>', StudentProfileHistoryApi.as_view(),
         name='student-profile-history'),
    path('/parent-profile/<uuid:parent_profile_id>', ParentProfileHistoryApi.as_view(), name='parent-profile-history'),
    path('/family/<uuid:family_id>', FamilyHistoryApi.as_view(), name='family-history'),
]
