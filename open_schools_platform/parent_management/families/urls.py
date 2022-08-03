from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.parent_management.families.views import FamilyApi, FamilyStudentProfilesListApi, \
    FamiliesListApi

urlpatterns = [
    path('',  MultipleViewManager({'get': FamiliesListApi,
                                  'post': FamilyApi}).as_view(), name='family-api'),
    path('<uuid:pk>/student-profiles', FamilyStudentProfilesListApi.as_view(), name='student-profiles-list')
]