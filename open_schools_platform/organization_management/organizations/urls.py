from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.organizations.views import OrganizationListApi, \
    OrganizationCreateApi, InviteEmployeeApi, InviteEmployeeUpdateApi, \
    OrganizationEmployeeQueriesListApi, OrganizationCircleQueriesListApi, OrganizationStudentsListApi, \
    OrganizationDeleteApi, GetStudentApi, OrganizationStudentProfilesExportApi, GetAnalytics, \
    OrganizationTeachersListApi, GetTeacherApi, OrganizationStudentProfileQueriesApi, OrganizationInvitedStudentsApi, \
    OrganizationCirclesListApi, OrganizationCirclesApi, FamilyOrganizationTicketsListApi, GetTicketsAnalytics

urlpatterns = [
    path('', MultipleViewManager({'get': OrganizationListApi,
                                  'post': OrganizationCreateApi}).as_view(), name='organization-api'),
    path('/<uuid:organization_id>/invite-employee', InviteEmployeeApi.as_view(), name='invite-employee'),
    path('/invite-employee', InviteEmployeeUpdateApi.as_view(), name='invite-employee-update'),
    path('/<uuid:organization_id>/invite-employee-queries', OrganizationEmployeeQueriesListApi.as_view(),
         name='queries-list'),
    path('/student-join-circle-query', OrganizationCircleQueriesListApi.as_view(), name='queries-list'),
    path('/students-invitations', OrganizationInvitedStudentsApi.as_view(), name='organization-students-invitations'),
    path('/students', OrganizationStudentsListApi.as_view(), name='students-list'),
    path('/<uuid:organization_id>', OrganizationDeleteApi.as_view(), name="delete-organization"),
    path('/students/<uuid:student_id>', GetStudentApi.as_view(), name='students'),
    path('/<uuid:organization_id>/students/export', OrganizationStudentProfilesExportApi.as_view(),
         name='export-organization-students'),
    path('/<uuid:organization_id>/analytics', GetAnalytics.as_view(), name='analytics'),
    path('/<uuid:organization_id>/ticket-analytics', GetTicketsAnalytics.as_view(), name='ticket-analytics'),
    path('/<uuid:organization>/student-profiles/<uuid:student_profile>/queries',
         OrganizationStudentProfileQueriesApi.as_view(), name='queries-organization-student-profile'),
    path('/<uuid:organization_id>/teachers', OrganizationTeachersListApi.as_view(), name='teachers-list'),
    path('/<uuid:organization_id>/circles', OrganizationCirclesListApi.as_view(), name='organization-circles-list'),
    path('/<uuid:organization_id>/family-tickets', FamilyOrganizationTicketsListApi.as_view(),
         name='organization-family-tickets-list'),
    path('/<uuid:organization_id>/circles/<uuid:circle_id>',
         OrganizationCirclesApi.as_view(), name='organization-circle'),
    path('/teachers/<uuid:teacher_id>', GetTeacherApi.as_view(), name='get-teacher')
]
