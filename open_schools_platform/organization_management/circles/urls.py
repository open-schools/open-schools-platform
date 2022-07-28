from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.circles.views import CreateCircleApi, GetCircles

urlpatterns = [
    path('', MultipleViewManager({'post': CreateCircleApi, 'get': GetCircles}).as_view(), name='circles'),
]
