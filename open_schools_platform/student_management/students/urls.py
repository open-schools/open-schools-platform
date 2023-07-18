from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.student_management.students.views import StudentProfileApi, AutoStudentJoinCircleQueryApi, \
    StudentJoinCircleQueryUpdateApi, StudentQueriesListApi, StudentCirclesListApi, StudentProfileUpdateApi, \
    StudentJoinCircleQueryApi, StudentDeleteApi, StudentProfileDeleteApi

urlpatterns = [
    path('/<uuid:student_id>', StudentDeleteApi.as_view(), name='delete-student'),
    path('/student-profile', StudentProfileApi.as_view(), name='create-student-profile'),
    path('/student-profile/<uuid:student_profile_id>',
         MultipleViewManager({'patch': StudentProfileUpdateApi, 'delete': StudentProfileDeleteApi}).as_view(),
         name='student-profile'),
    path('/student-profile-generate/student-join-cricle-query', AutoStudentJoinCircleQueryApi.as_view(),
         name='auto-student-join-circle-query'),
    path('/student-profile/<uuid:student_profile_id>/student-join-circle-query', StudentJoinCircleQueryApi.as_view(),
         name='student-join-circle-query'),
    path('/student-join-circle-query', StudentJoinCircleQueryUpdateApi.as_view(),
         name='student-join-circle-update-query'),
    path('/student-profile/<uuid:student_profile_id>/queries', StudentQueriesListApi.as_view(), name='queries-list'),
    path('/student-profile/<uuid:student_profile_id>/circles', StudentCirclesListApi.as_view(), name='circles-list'),
]
