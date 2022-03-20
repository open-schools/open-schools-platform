import django_filters

from open_schools_platform.users.models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ('id', 'phone')
