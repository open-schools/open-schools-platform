from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.employees.views import EmployeeListApi, EmployeeQueriesListApi, \
    EmployeeUpdateApi, EmployeeDeleteApi, EmployeeProfileUpdateApi, EmployeeGetApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
    path('/employee-profile/<uuid:employee_profile_id>',
         MultipleViewManager({'patch': EmployeeProfileUpdateApi}).as_view(), name='employee-profile'),
    path('/<uuid:employee_id>',
         MultipleViewManager({'get': EmployeeGetApi, 'patch': EmployeeUpdateApi, 'delete': EmployeeDeleteApi}).as_view(), name='employee'),
    path('/employee-profile/get-invitations', EmployeeQueriesListApi.as_view(), name='employee_query-list'),
]
