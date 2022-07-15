import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from open_schools_platform.common.models import BaseModel


class Query(BaseModel):
    class Status(models.TextChoices):
        ACCEPTED = 'ACCEPTED', 'Accepted'
        SENT = 'SENT', 'Sent'
        IN_PROGRESS = 'IN_PROGRESS', 'In progress'
        DECLINED = "DECLINED", 'Declined'
        CANCELED = "CANCELED", 'Canceled'

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    recipient_ct = models.ForeignKey(ContentType, related_name="recipient_ct", null=True, on_delete=models.CASCADE)
    recipient_id = models.UUIDField(default=uuid.uuid4)

    recipient = GenericForeignKey('recipient_ct', 'recipient_id')

    sender_ct = models.ForeignKey(ContentType, related_name="sender_ct", null=True, on_delete=models.CASCADE)
    sender_id = models.UUIDField(default=uuid.uuid4)

    sender = GenericForeignKey('sender_ct', 'sender_id')

    body_ct = models.ForeignKey(ContentType, related_name="body_ct", null=True, on_delete=models.CASCADE)
    body_id = models.UUIDField(default=uuid.uuid4)

    body = GenericForeignKey('body_ct', 'body_id')

    status = models.CharField(
        max_length=200,
        choices=Status.choices,
        default=Status.SENT,
    )

    class Meta:
        unique_together = ('recipient_ct', 'recipient_id', 'sender_ct', 'sender_id')
