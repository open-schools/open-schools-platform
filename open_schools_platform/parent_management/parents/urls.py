from django.urls import path

from open_schools_platform.parent_management.parents.views import InviteParentQueriesListApi

urlpatterns = [
    path('get-invitations',  InviteParentQueriesListApi.as_view(), name='invite-parent-list'),
]
