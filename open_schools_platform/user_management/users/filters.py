from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.user_management.users.models import User, CreationToken, FirebaseNotificationToken


class UserFilter(BaseFilterSet):
    class Meta:
        model = User
        fields = ('id', 'phone')


class CreationTokenFilter(BaseFilterSet):
    class Meta:
        model = CreationToken
        fields = ('key', 'phone')


class FirebaseTokenFilter(BaseFilterSet):
    class Meta:
        model = FirebaseNotificationToken
        fields = ('id', 'token', 'user')
