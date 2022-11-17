from django.urls import path

from open_schools_platform.history_management.views import *

urlpatterns = [
    path('user/<uuid:pk>', UserHistoryApi.as_view(), name='user_history'),
    path('organization/<uuid:pk>', OrganizationHistoryApi.as_view(), name='organization_history'),
    path('employee/<uuid:pk>', EmployeeHistoryApi.as_view(), name='employee_history'),
    path('circle/<uuid:pk>', CircleHistoryApi.as_view(), name='circle_history'),
    path('student/<uuid:pk>', StudentHistoryApi.as_view(), name='student_history'),
]
