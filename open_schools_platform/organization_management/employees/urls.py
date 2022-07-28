from django.urls import path

from open_schools_platform.organization_management.employees.views import EmployeeListApi, EmployeeQueriesListApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
    path('employee-profile/get-invitations', EmployeeQueriesListApi.as_view(), name='employee_query_list'),
]
