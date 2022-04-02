from django.urls import path, include

user_management_urls = [
    path('users/', include(('open_schools_platform.users.urls', 'users'))),
]

urlpatterns = [
    path(
        'auth/', include(('open_schools_platform.authentication.urls', 'authentication'))
    ),
    path('user-management/', include(user_management_urls)),
    path('errors/', include(('open_schools_platform.errors.urls', 'errors'))),
]
