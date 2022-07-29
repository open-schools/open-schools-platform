from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.circles.views import CreateCircleApi, GetCircles, \
    CirclesQueriesListApi

urlpatterns = [
    path('', MultipleViewManager({'post': CreateCircleApi, 'get': GetCircles}).as_view(), name='circles'),
    path('<uuid:pk>/queries', CirclesQueriesListApi.as_view(), name='queries-list')
]
