from django.urls import path

from .views import UserApi, CreationTokenApi, VerificationApi

urlpatterns = [
    path('user/token', CreationTokenApi.as_view(), name='token'),
    path('user/token/verify', VerificationApi.as_view(), name='verification-phone-by-token'),
    path('user', UserApi.as_view(), name='user'),
]

