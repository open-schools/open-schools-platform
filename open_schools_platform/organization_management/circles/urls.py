from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.organization_management.circles.views import CreateCircleApi, GetCirclesApi, \
    CirclesQueriesListApi, CirclesStudentsListApi, GetCircleApi, InviteStudentApi, CircleDeleteApi, \
    CirclesStudentProfilesExportApi, InviteTeacherApi, CircleICalExportApi, CirclesICalExportApi, UpdateCircleApi

urlpatterns = [
    path('', MultipleViewManager({'get': GetCirclesApi, 'post': CreateCircleApi}).as_view(), name='circles'),
    path('/ical', CirclesICalExportApi.as_view(), name='circles-ical'),
    path('/<uuid:circle_id>',
         MultipleViewManager({'get': GetCircleApi, 'delete': CircleDeleteApi, 'patch': UpdateCircleApi}).as_view(),
         name='circle'),
    path('/<uuid:circle_id>/queries', CirclesQueriesListApi.as_view(), name='queries-list'),
    path('/<uuid:circle_id>/students', CirclesStudentsListApi.as_view(), name='students-list'),
    path('/<uuid:circle_id>/invite-student', InviteStudentApi.as_view(), name='invite-student'),
    path('/<uuid:circle_id>/invite-teacher', InviteTeacherApi.as_view(), name='invite-teacher'),
    path('/<uuid:circle_id>/students/export', CirclesStudentProfilesExportApi.as_view(), name='students-export'),
    path('/<uuid:circle_id>/ical', CircleICalExportApi.as_view(), name='circle-ical'),
]
