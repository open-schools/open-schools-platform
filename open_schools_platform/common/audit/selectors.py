# common/audit/selectors.py
from django.db.models import Q
from .models import AuditLog
from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.common.filters import ComplexFilter


@selector_factory(AuditLog)
def get_audit_logs(*, filters=None, prefetch_related_list=None, order_by='-created_at'):
    """Получение логов аудита с фильтрацией"""
    filters = filters or {}

    qs = AuditLog.objects.prefetch_related(*(prefetch_related_list or [])).all()

    # Фильтрация по типу события
    if event_type := filters.get('event_type'):
        qs = qs.filter(event_type=event_type)

    # Фильтрация по пользователю
    if user_id := filters.get('user_id'):
        qs = qs.filter(user_id=user_id)

    # Фильтрация по приложению
    if app_id := filters.get('app_id'):
        qs = qs.filter(app_id=app_id)

    # Фильтрация по организации
    if organization_id := filters.get('organization_id'):
        qs = qs.filter(organization_id=organization_id)

    # Фильтрация по дате
    if date_from := filters.get('date_from'):
        qs = qs.filter(created_at__date__gte=date_from)

    if date_to := filters.get('date_to'):
        qs = qs.filter(created_at__date__lte=date_to)

    # Поиск по описанию
    if search := filters.get('search'):
        qs = qs.filter(Q(description__icontains=search) | Q(metadata__icontains=search))

    # Сортировка
    if order_by:
        qs = qs.order_by(order_by)

    return qs


@selector_factory(AuditLog)
def get_audit_log(*, filters=None, prefetch_related_list=None):
    """Получение одного лога аудита"""
    filters = filters or {}

    qs = AuditLog.objects.prefetch_related(*(prefetch_related_list or [])).all()

    for key, value in filters.items():
        qs = qs.filter(**{key: value})

    return qs.first()


# Комплексный фильтр для использования в API
audit_logs_filter = ComplexFilter(
    selector=get_audit_logs,
    include_list=["event_type", "user_id", "app_id", "organization_id", "date_from", "date_to", "search"]
)