from typing import Optional, Union, Tuple, Type, Any  # noqa: F401
from safedelete.queryset import SafeDeleteQueryset  # noqa: F401
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel


class Query(BaseModel):
    class Status(models.TextChoices):  # type: ignore[misc,name-defined]
        ACCEPTED = "ACCEPTED"
        SENT = "SENT"
        IN_PROGRESS = "IN_PROGRESS"
        DECLINED = "DECLINED"
        CANCELED = "CANCELED"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    recipient_ct = models.ForeignKey(ContentType, related_name="recipient_ct", null=True, on_delete=models.CASCADE)
    recipient_id = models.UUIDField(default=uuid.uuid4)

    recipient = GenericForeignKey("recipient_ct", "recipient_id")

    sender_ct = models.ForeignKey(ContentType, related_name="sender_ct", null=True, on_delete=models.CASCADE)
    sender_id = models.UUIDField(default=uuid.uuid4)

    sender = GenericForeignKey("sender_ct", "sender_id")

    body_ct = models.ForeignKey(ContentType, related_name="body_ct", null=True, blank=True, on_delete=models.CASCADE)
    body_id = models.UUIDField(default=uuid.uuid4)

    body = GenericForeignKey("body_ct", "body_id")

    additional_ct = models.ForeignKey(ContentType, related_name="additional_ct", on_delete=models.CASCADE,
                                      null=True, blank=True)
    additional_id = models.UUIDField(default=uuid.uuid4)

    additional = GenericForeignKey("additional_ct", "additional_id")

    status = models.CharField(
        max_length=200,
        choices=Status.choices,
        default=Status.SENT,
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.id.__str__()

    @staticmethod
    def get_all_statuses() -> list:
        return list(Query.Status.__dict__["_member_map_"].keys())
