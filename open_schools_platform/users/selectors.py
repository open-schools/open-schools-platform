from django.db.models.query import QuerySet

from open_schools_platform.users.models import User, CreationToken
from open_schools_platform.users.filters import UserFilter


def user_get_login_data(*, user: User):
    return {
        'id': user.id,
        'email': user.email,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'is_superuser': user.is_superuser,
    }


def user_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs


def get_user_by_phone(phone) -> User or None:
    try:
        user = User.objects.get(phone=phone)
    except:
        return None
    return user


def get_token_by_id(token) -> CreationToken or None:
    try:
        creation_token = CreationToken.objects.get(token=token)
    except:
        return None
    return creation_token


def get_token_by_phone(phone) -> CreationToken or None:
    try:
        token = CreationToken.objects.\
            filter(phone=phone).\
            order_by('created_at')[::-1][0]
    except:
        return None
    return token
