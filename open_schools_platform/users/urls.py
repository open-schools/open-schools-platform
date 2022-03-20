from django.urls import path

from .views import UserApi, CreationTokenApi

urlpatterns = [
    path('user/token', CreationTokenApi.as_view(), name='user'),
    path('user', UserApi.as_view(), name='user')
]

