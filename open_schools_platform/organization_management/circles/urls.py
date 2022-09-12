from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.circles.views import CreateCircleApi, GetCirclesApi, \
    CirclesQueriesListApi, CirclesStudentsListApi, GetCircleApi

urlpatterns = [
    path('', MultipleViewManager({'get': GetCirclesApi, 'post': CreateCircleApi}).as_view(), name='circles'),
    path('<uuid:pk>', GetCircleApi.as_view(), name='get-circle'),
    path('<uuid:pk>/queries', CirclesQueriesListApi.as_view(), name='queries-list'),
    path('<uuid:pk>/students', CirclesStudentsListApi.as_view(), name='students-list')
]
