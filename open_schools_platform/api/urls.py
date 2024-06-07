from django.urls import path, include
from django.conf import settings


query_management_urls = [
    path('queries', include(('open_schools_platform.query_management.queries.urls', 'queries'))),
]

parent_management_urls = [
    path('families', include(('open_schools_platform.parent_management.families.urls', 'families'))),
    path('parents', include(("open_schools_platform.parent_management.parents.urls", 'parents'))),
]

user_management_urls = [
    path('users', include(('open_schools_platform.user_management.users.urls', 'users'))),
    path(
        'auth', include(('open_schools_platform.user_management.authentication.urls', 'authentication'))
    ),
]

organization_management_urls = [
    path('organizations',
         include(('open_schools_platform.organization_management.organizations.urls', 'organizations'))),
    path('employees',
         include(('open_schools_platform.organization_management.employees.urls', 'employees'))),
    path('circles',
         include(('open_schools_platform.organization_management.circles.urls', 'circles'))),
    path('teachers',
         include(('open_schools_platform.organization_management.teachers.urls', 'teachers'))),
]

students_management_urls = [
    path('students', include(('open_schools_platform.student_management.students.urls', 'students')))
]

photos_management_urls = [
    path('photos', include(('open_schools_platform.photo_management.photos.urls', 'photos')))
]

history_management_urls = [
    path('history', include(('open_schools_platform.history_management.urls', 'history'))),
]

ticket_management_urls = [
    path('ticket', include(('open_schools_platform.ticket_management.tickets.urls', 'ticket'))),
]

urlpatterns = [
    path('user-management/', include((user_management_urls, 'user-management'))),
    path('organization-management/', include((organization_management_urls, 'organization-management'))),
    path('query-management/', include((query_management_urls, 'query-management'))),
    path('parent-management/', include((parent_management_urls, 'parent-management'))),
    path('students-management/', include((students_management_urls, 'students-management'))),
    path('photos-management/', include((photos_management_urls, 'photo-management'))),
    path('history-management/', include((history_management_urls, 'history-management'))),
    path('ticket-management/', include((ticket_management_urls, 'ticket-management')))
]

if settings.SWAGGER_ENABLED:
    urlpatterns += [path('errors/', include(('open_schools_platform.errors.urls', 'errors')))]
