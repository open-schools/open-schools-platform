from django.urls import path

from open_schools_platform.organization_management.circles.views import CreateCircleApi

urlpatterns = [
    path('', CreateCircleApi.as_view(), name='create-circle')
]
