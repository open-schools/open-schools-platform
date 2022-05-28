from django.urls import path

from open_schools_platform.organization_management.employees.views import EmployeeApi

urlpatterns = [
    path('', EmployeeApi.as_view(), name='employee'),
]
