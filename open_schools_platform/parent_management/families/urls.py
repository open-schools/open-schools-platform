from django.urls import path

from open_schools_platform.parent_management.families.views import FamilyApi

urlpatterns = [
    path('', FamilyApi.as_view(), name='create-family')
]
