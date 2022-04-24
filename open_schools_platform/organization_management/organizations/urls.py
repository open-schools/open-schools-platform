from django.urls import path

from open_schools_platform.organization_management.organizations.views import OrganizationApi  # type: ignore

urlpatterns = [
    path('', OrganizationApi.as_view(), name='organization_api'),
]
