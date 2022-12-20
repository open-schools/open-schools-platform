from django.urls import path

from open_schools_platform.photo_management.photos.views import PhotoApi

urlpatterns = [
    path('/photo/<uuid:pk>', PhotoApi.as_view(), name='create-photo'),
]
