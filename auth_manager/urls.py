from django.urls import re_path

from auth_manager import views


urlpatterns = [
    re_path(r"^users/create", views.UserProfileCreateView.as_view(), name="users"),
    re_path(r"^users/verify", views.UserProfileCreateView.as_view(), name="users"),
]