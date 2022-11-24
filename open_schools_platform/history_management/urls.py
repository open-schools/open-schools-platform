from django.urls import path

from open_schools_platform.history_management.views import UserHistoryApi, OrganizationHistoryApi, EmployeeHistoryApi, \
    CircleHistoryApi, StudentHistoryApi, StudentProfileHistoryApi, EmployeeProfileHistory, ParentProfileHistory,\
    FamilyHistory

urlpatterns = [
    path('user/<uuid:pk>', UserHistoryApi.as_view(), name='user_history'),
    path('organization/<uuid:pk>', OrganizationHistoryApi.as_view(), name='organization_history'),
    path('employee/<uuid:pk>', EmployeeHistoryApi.as_view(), name='employee_history'),
    path('employee-profile/<uuid:pk>', EmployeeProfileHistory.as_view(), name='employee-profile_history'),
    path('circle/<uuid:pk>', CircleHistoryApi.as_view(), name='circle_history'),
    path('student/<uuid:pk>', StudentHistoryApi.as_view(), name='student_history'),
    path('student-profile/<uuid:pk>', StudentProfileHistoryApi.as_view(), name='student-profile_history'),
    path('parent-profile/<uuid:pk>', ParentProfileHistory.as_view(), name='parent-profile_history'),
    path('family/<uuid:pk>', FamilyHistory.as_view(), name='family_history'),
]
