from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.organizations.views import OrganizationListApi, \
    OrganizationCreateApi, InviteEmployeeApi, InviteEmployeeUpdateApi, \
    OrganizationEmployeeQueriesListApi, OrganizationCircleQueriesListApi, OrganizationStudentsListApi, \
    OrganizationDeleteApi

urlpatterns = [
    path('', MultipleViewManager({'get': OrganizationListApi,
                                  'post': OrganizationCreateApi}).as_view(), name='organization-api'),
    path('<uuid:pk>/invite-employee', InviteEmployeeApi.as_view(), name='invite-employee'),
    path('invite-employee', InviteEmployeeUpdateApi.as_view(), name='invite-employee-update'),
    path('<uuid:pk>/invite-employee-queries', OrganizationEmployeeQueriesListApi.as_view(), name='queries-list'),
    path('student-join-circle-query', OrganizationCircleQueriesListApi.as_view(), name='queries-list'),
    path('students', OrganizationStudentsListApi.as_view(), name='students-list'),
    path('delete/<uuid:pk>', OrganizationDeleteApi.as_view(), name="delete_organization")
]
