from django.urls import path

from open_schools_platform.organization_management.employees.views import EmployeeListApi, EmployeeQueriesListApi, \
    EmployeeUpdateApi, EmployeeDeleteApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
    path('<uuid:pk>', EmployeeUpdateApi.as_view(), name='update_employee'),
    path('employee-profile/get-invitations', EmployeeQueriesListApi.as_view(), name='employee_query_list'),
    path('delete/<uuid:pk>', EmployeeDeleteApi.as_view(), name='delete_employee')
]
