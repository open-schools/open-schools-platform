from django.utils.translation import gettext_lazy as _
from django.db import models


class EmployeeRole(models.TextChoices):
    creator = 'creator', _('creator')
    director = 'director', _('director')
    employee = 'employee', _('employee')
    view_only = 'view_only', _('view only')


# defines which role can be replaced for a given key
role_hierarchy = {
    'creator': ('creator',),
    'director': ('director', 'creator'),
    'employee': ('employee', 'director', 'creator'),
    'view_only': ('view_only', 'employee', 'director', 'creator')
}
