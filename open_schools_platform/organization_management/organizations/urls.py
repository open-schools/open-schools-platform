from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.organizations.views import \
    OrganizationListApi, OrganizationCreateApi  # type: ignore

urlpatterns = [
    path('', MultipleViewManager({'get': OrganizationListApi,
                                  'post': OrganizationCreateApi}).as_view(), name='organization_api'),
]
