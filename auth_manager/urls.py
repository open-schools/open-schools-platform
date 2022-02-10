from django.urls import re_path

from auth_manager import views

urlpatterns = [
    re_path(r"^users?", views.UserProfileView.as_view(), name="users"),
]