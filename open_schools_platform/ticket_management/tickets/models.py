from open_schools_platform.common.models import BaseModel, BaseManager
from django.db import models
import uuid

from open_schools_platform.query_management.queries.models import Query


class TicketManager(BaseManager):
    pass


class TicketCommentManager(BaseManager):
    pass


class Ticket(Query):
    @property
    def last_comment(self):
        return self.comments.first()

    @property
    def unread_sender_comments_count(self):
        return len(self.comments.filter(is_seen=False, is_sender=True))

    @property
    def unread_recipient_comments_count(self):
        return len(self.comments.filter(is_seen=False, is_sender=False))

    objects = TicketManager()  # type: ignore[assignment]

    def __str__(self):
        return self.id.__str__()


class TicketComment(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    ticket = models.ForeignKey(Ticket, related_name="comments", on_delete=models.CASCADE)

    is_sender = models.BooleanField()
    is_seen = models.BooleanField(default=False)
    value = models.CharField(max_length=1400)

    objects = TicketCommentManager()  # type: ignore[assignment]

    def __str__(self):
        return self.value[0:100]
