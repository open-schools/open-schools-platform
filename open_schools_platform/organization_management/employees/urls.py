from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.employees.views import EmployeeListApi, EmployeeQueriesListApi, \
    EmployeeUpdateApi, EmployeeDeleteApi

urlpatterns = [
    path('', EmployeeListApi.as_view(), name='employees'),
    path('/<uuid:pk>',
         MultipleViewManager({'patch': EmployeeUpdateApi, 'delete': EmployeeDeleteApi}).as_view(), name='employee'),
    path('/employee-profile/get-invitations', EmployeeQueriesListApi.as_view(), name='employee_query-list'),
]
