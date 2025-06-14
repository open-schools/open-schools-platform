from typing import Dict, Optional

from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.receipt_management.receipts.filters import ReceiptFilter, ReceiptNotificationFilter
from open_schools_platform.receipt_management.receipts.models import Receipt, ReceiptNotification
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


@selector_factory(Receipt)
def get_receipts(*, filters=None, prefetch_related_list=None) -> QuerySet:
    """
    Get receipts with filtering support.
    """
    filters = filters or {}
    prefetch_related_list = prefetch_related_list or []

    qs = Receipt.objects.prefetch_related(*prefetch_related_list).all()
    receipts = ReceiptFilter(filters, qs).qs

    return receipts


@selector_factory(Receipt)
def get_receipt(*, filters=None, user: User = None, prefetch_related_list=None) -> Receipt:
    """
    Get a single receipt with permission checks.
    """
    filters = filters or {}
    prefetch_related_list = prefetch_related_list or []

    qs = Receipt.objects.prefetch_related(*prefetch_related_list).all()
    receipt = ReceiptFilter(filters, qs).qs.first()

    if user and receipt and not user.has_perm("receipts.receipt_access", receipt):
        raise PermissionDenied

    return receipt


@selector_factory(ReceiptNotification)
def get_receipt_notifications(*, filters=None, prefetch_related_list=None) -> QuerySet:
    """
    Get receipt notifications with filtering support.
    """
    filters = filters or {}
    prefetch_related_list = prefetch_related_list or []

    qs = ReceiptNotification.objects.prefetch_related(*prefetch_related_list).all()
    notifications = ReceiptNotificationFilter(filters, qs).qs

    return notifications.order_by('-sent_at')

def get_overdue_receipts() -> QuerySet:
    """
    Get all overdue receipts for system-wide processing.
    """
    from django.utils import timezone

    return Receipt.objects.filter(
        payment_due_date__lt=timezone.now().date(),
        total_amount__gt=0
    ).order_by('payment_due_date')


def get_receipts_for_family(family: Family, filters: Dict = None) -> QuerySet[Receipt]:
    """
    Get receipts for all students in a family
    """
    filters = filters or {}

    student_profiles = family.student_profiles.all()
    qs = Receipt.objects.filter(student_profile__in=student_profiles)

    if filters:
        qs = qs.filter(**filters)

    return qs.order_by('-created_at')


def get_receipts_for_student_profile(student_profile: StudentProfile, filters: Dict = None) -> QuerySet[Receipt]:
    """
    Get receipts for a specific student profile
    """
    filters = filters or {}

    qs = Receipt.objects.filter(student_profile=student_profile)

    if filters:
        qs = qs.filter(**filters)

    return qs.order_by('-created_at')


def get_overdue_receipts_for_family(family: Family) -> QuerySet[Receipt]:
    """
    Get overdue receipts for a family
    """
    from django.utils import timezone
    today = timezone.now().date()

    return get_receipts_for_family(family, {
        'payment_due_date__lt': today,
        'total_amount__gt': 0
    })


def get_recent_receipts_for_family(family: Family, days: int = 30) -> QuerySet[Receipt]:
    """
    Get recent receipts for a family
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    return get_receipts_for_family(family, {
        'created_at__gte': cutoff_date
    })


@selector_factory(Receipt)
def get_receipts_with_filters(user: User, filters: Dict = None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}
    prefetch_related_list = prefetch_related_list or []

    qs = Receipt.objects.prefetch_related(*prefetch_related_list).all()

    receipts = ReceiptFilter(filters, qs).qs

    return receipts.order_by('-created_at')


def get_single_receipt_notification(*, filters: Dict = None, empty_exception=False) -> Optional[ReceiptNotification]:
    """
    Get single receipt notification by filters
    """
    filters = filters or {}

    try:
        return ReceiptNotification.objects.get(**filters)
    except ReceiptNotification.DoesNotExist:
        if empty_exception:
            from open_schools_platform.errors.exceptions import NotFound
            raise NotFound("Receipt notification not found")
        return None


def get_notifications_list(*, filters: Dict = None) -> QuerySet[ReceiptNotification]:
    """
    Get receipt notifications by filters
    """
    filters = filters or {}

    qs = ReceiptNotification.objects.all()

    if filters:
        qs = qs.filter(**filters)

    return qs.order_by('-sent_at')


def get_notifications_for_receipt(receipt: Receipt) -> QuerySet[ReceiptNotification]:
    """
    Get all notifications for a specific receipt
    """
    return ReceiptNotification.objects.filter(receipt=receipt).order_by('-sent_at')


def get_recent_notifications(days: int = 7) -> QuerySet[ReceiptNotification]:
    """
    Get notifications from the last N days
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    return ReceiptNotification.objects.filter(
        sent_at__gte=cutoff_date
    ).order_by('-sent_at')


def get_failed_notifications() -> QuerySet[ReceiptNotification]:
    """
    Get notifications that failed to deliver
    """
    return ReceiptNotification.objects.filter(is_delivered=False)


def get_receipt_statistics_for_family(family: Family) -> Dict:
    """
    Get receipt statistics for a family
    """
    receipts = get_receipts_for_family(family)
    total_receipts = receipts.count()
    overdue_receipts = get_overdue_receipts_for_family(family).count()

    total_amount = sum(receipt.total_amount for receipt in receipts)
    overdue_amount = sum(receipt.total_amount for receipt in get_overdue_receipts_for_family(family))

    return {
        'total_receipts': total_receipts,
        'overdue_receipts': overdue_receipts,
        'total_amount': total_amount,
        'overdue_amount': overdue_amount,
    }


def get_receipt_statistics_for_student(student_profile: StudentProfile) -> Dict:
    """
    Get receipt statistics for a student
    """
    receipts = get_receipts_for_student_profile(student_profile)
    total_receipts = receipts.count()

    from django.utils import timezone
    today = timezone.now().date()
    overdue_receipts = receipts.filter(
        payment_due_date__lt=today,
        total_amount__gt=0
    ).count()

    total_amount = sum(receipt.total_amount for receipt in receipts)
    overdue_amount = sum(
        receipt.total_amount for receipt in receipts.filter(
            payment_due_date__lt=today,
            total_amount__gt=0
        )
    )

    return {
        'total_receipts': total_receipts,
        'overdue_receipts': overdue_receipts,
        'total_amount': total_amount,
        'overdue_amount': overdue_amount,
    }
