from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.parent_management.families.views import FamilyApi, FamilyStudentProfilesListApi, \
    FamiliesListApi, FamilyDeleteApi, InviteParentApi, FamilyStudentInvitesListApi, FamiliesStudentInvitesListApi

urlpatterns = [
    path('', MultipleViewManager({'get': FamiliesListApi, 'post': FamilyApi}).as_view(), name='family-api'),
    path('/<uuid:family_id>/student-profiles', FamilyStudentProfilesListApi.as_view(), name='student-profiles-list'),
    path('/invite-parent', InviteParentApi.as_view(), name='invite-parent'),
    path('/<uuid:family_id>', FamilyDeleteApi.as_view(), name="delete-family"),
    path('/<uuid:family_id>/student-invitations', FamilyStudentInvitesListApi.as_view(),
         name="family-student-invitations-list"),
    path('/student-invitations', FamiliesStudentInvitesListApi.as_view(),
         name="all-student-invitations-list")
]
