from django.urls import path

from open_schools_platform.student_management.student_profile.views import StudentProfileApi

urlpatterns = [
    path('student-profile', StudentProfileApi.as_view(), name='create-student-profile')
]