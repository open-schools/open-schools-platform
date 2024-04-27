from django.urls import path

from open_schools_platform.parent_management.parents.views import InviteParentQueriesListApi, \
    StudentJoinCircleQueriesListApi, GetAccessibleOrganizationListApi, FamilyOrganizationTicketsListApi, \
    FamilyOrganizationTicketCommentsListApi

urlpatterns = [
    path('/get-invitations', InviteParentQueriesListApi.as_view(), name='invite-parent-list'),
    path('/get-organization-tickets', FamilyOrganizationTicketsListApi.as_view(),
         name='organization-tickets-list'),
    path('/<uuid:organization_id>/get-ticket-comments', FamilyOrganizationTicketCommentsListApi.as_view(),
         name='organization-ticket-comments-list'),
    path('/get-accessible-organizations', GetAccessibleOrganizationListApi.as_view(),
         name='accessible-organizations-list'),
    path('/student-join-circle-queries', StudentJoinCircleQueriesListApi.as_view(),
         name='student-join-circle-queries-list'),
]
