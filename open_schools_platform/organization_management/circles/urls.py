from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.circles.views import CreateCircleApi, GetCirclesApi, \
    CirclesQueriesListApi, CirclesStudentsListApi, GetCircleApi, InviteStudentApi, CircleDeleteApi

urlpatterns = [
    path('', MultipleViewManager({'get': GetCirclesApi, 'post': CreateCircleApi}).as_view(), name='circles'),
    path('<uuid:pk>', MultipleViewManager({'get': GetCircleApi, 'delete': CircleDeleteApi}).as_view(), name='circle'),
    path('<uuid:pk>/queries', CirclesQueriesListApi.as_view(), name='queries-list'),
    path('<uuid:pk>/students', CirclesStudentsListApi.as_view(), name='students-list'),
    path('<uuid:pk>/invite-student', InviteStudentApi.as_view(), name='invite-student'),
]
