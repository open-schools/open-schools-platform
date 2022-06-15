from django.urls import path, include

from .apis import (
    UserJwtLoginApi,
    UserJwtLogoutApi,

    UserMeApi,
    UpdatePasswordApi
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
        include(([
             path(
                 "change-password/",
                 UpdatePasswordApi.as_view(),
                 name="change-password"
             ),
             path(
                 "",
                 UserMeApi.as_view(),
                 name="me"
             )
         ]))
    )
]