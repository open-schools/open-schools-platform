from django.db.models.query import QuerySet

from open_schools_platform.users.models import User, CreationToken
from open_schools_platform.users.filters import UserFilter, CreationTokenFilter


def user_get_login_data(*, user: User):
    return {
        'id': user.id,
        'phone': user.phone,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'is_superuser': user.is_superuser,
    }


def get_user(*, filters=None) -> User:
    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs.first()


def get_token(*, filters=None) -> CreationToken:
    filters = filters or {}

    qs = CreationToken.objects.all().order_by('created_at')

    return CreationTokenFilter(filters, qs).qs.last()
