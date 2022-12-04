from django.urls import path, include

from .views import (
    UserJwtLoginApi,
    UserJwtLogoutApi,

    UserMeApi,
    UpdatePasswordApi
)

urlpatterns = [
    path(
        '/jwt/',
        include(([
            path(
                "login",
                UserJwtLoginApi.as_view(),
                name="login"
            ),
            path(
                "logout",
                UserJwtLogoutApi.as_view(),
                name="logout"
            )
        ], "jwt"))
    ),
    path(
        '/me',
        include(([
             path(
                 "/update-password",
                 UpdatePasswordApi.as_view(),
                 name="update-password"
             ),
             path(
                 "",
                 UserMeApi.as_view(),
                 name="info"
             )
         ], "me"))
    )
]
