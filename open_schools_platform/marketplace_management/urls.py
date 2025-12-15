from django.urls import path

from open_schools_platform.marketplace_management.views import AppApi

urlpatterns = [
    path('/apps/', AppApi.as_view({"get": "list"}), name='miniapps-list')
]