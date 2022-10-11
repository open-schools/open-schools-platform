from django.urls import path

from open_schools_platform.photo_management.photos.views import PhotoApi

urlpatterns = [
    path('photo', PhotoApi.as_view(), name='create-photo'), ]
