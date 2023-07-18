from django.urls import path

from .views import UserApi, CreationTokenApi, VerificationApi, CodeResendApi, RetrieveCreationTokenApi, \
    UserResetPasswordApi, AddFCMNotificationTokenApi

urlpatterns = [
    path('/token', CreationTokenApi.as_view(), name='create-token'),
    path('/token/<uuid:token_key>', RetrieveCreationTokenApi.as_view(), name='get-token'),
    path('/token/<uuid:token_key>/verify', VerificationApi.as_view(), name='verification-phone-by-token'),
    path('', UserApi.as_view(), name='user'),
    path('/token/<uuid:token_key>/resend', CodeResendApi.as_view(), name='resend'),
    path('/reset-password', UserResetPasswordApi.as_view(), name='reset-password'),
    path('/firebase-notification-token', AddFCMNotificationTokenApi.as_view(), name='add-firebase-notification-token')
]
