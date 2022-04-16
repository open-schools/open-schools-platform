from django.urls import path, include

user_management_urls = [
    path('users/', include(('open_schools_platform.user_management.users.urls', 'users'))),
    path(
        'auth/', include(('open_schools_platform.user_management.authentication.urls', 'authentication'))
    ),
]

urlpatterns = [
    path('user-management/', include(user_management_urls)),
    path('errors/', include(('open_schools_platform.errors.urls', 'errors'))),
]
