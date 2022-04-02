import django_filters

from open_schools_platform.users.models import User, CreationToken


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ('id', 'phone')


class CreationTokenFilter(django_filters.FilterSet):
    class Meta:
        model = CreationToken
        fields = ('key', 'phone')
