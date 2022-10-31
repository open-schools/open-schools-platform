from django.urls import path

from open_schools_platform.organization_management.employees.views import EmployeeListApi, EmployeeQueriesListApi, \
    EmployeeEditApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
    path('<uuid:pk>', EmployeeEditApi.as_view(), name='edit-employee'),
    path('employee-profile/get-invitations', EmployeeQueriesListApi.as_view(), name='employee_query-list'),
]
