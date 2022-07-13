from django.urls import path

from open_schools_platform.organization_management.employees.views import EmployeeListApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
]
