from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.employees.views import EmployeeCreateApi, \
    EmployeeListApi

urlpatterns = [
    path('', MultipleViewManager({"get": EmployeeCreateApi,
                                  "post": EmployeeListApi}).as_view(), name='employee'),
]
