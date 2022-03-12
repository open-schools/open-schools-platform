from django.urls import path, include

urlpatterns = [
    path(
        'auth/', include(('open_schools_platform.authentication.urls', 'authentication'))
    ),
    path('users/', include(('open_schools_platform.users.urls', 'users'))),
    path('errors/', include(('open_schools_platform.errors.urls', 'errors'))),
]
