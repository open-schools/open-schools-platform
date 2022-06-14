from django.urls import path, include

from .apis import (
    UserJwtLoginApi,
    UserJwtLogoutApi,

    UserMeApi,
)

urlpatterns = [
    path(
        'jwt/',
        include(([
            path(
                "login/",
                UserJwtLoginApi.as_view(),
                name="login"
            ),
            path(
                "logout/",
                UserJwtLogoutApi.as_view(),
                name="logout"
            )
        ], "jwt"))
    ),
    path(
        'me/',
        UserMeApi.as_view(),
        name='me'
    )
]
