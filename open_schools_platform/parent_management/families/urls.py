from django.urls import path

from open_schools_platform.parent_management.families.views import FamilyApi, FamilyStudentProfilesListApi

urlpatterns = [
    path('', FamilyApi.as_view(), name='families'),
    path('<uuid:pk>', FamilyStudentProfilesListApi.as_view(), name='student_profiles-list')
]
