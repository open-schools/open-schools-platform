import uuid

from typing import Any

from open_schools_platform.common.models import BaseModel
from django.db import models

from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update


class OrganizationManager(models.Manager):
    def create(self, *args: Any, **kwargs: Any):
        organization = self.model(
            *args,
            **kwargs,
        )

        organization.full_clean()
        organization.save(using=self._db)

        return organization


class OrganizationQueryHandler:
    @staticmethod
    def query_handler(query: Query, new_status: str):
        # TODO: Disable some statuses for some models here
        if query.status == new_status:
            return query.body
        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            query.body.organization = query.sender  # type: ignore
            query.body.employee_profile = query.recipient  # type: ignore
            query.body.save()  # type: ignore

        return query.body


class Organization(BaseModel, OrganizationQueryHandler):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=255)

    objects = OrganizationManager()

    def __str__(self):
        return self.name
