import uuid

from typing import Any


from open_schools_platform.common.models import BaseModel, BaseManager
from django.db import models


class TestModelManager(BaseManager):
    def create(self, *args: Any, **kwargs: Any):
        test_model = self.model(
            *args,
            **kwargs,
        )

        test_model.full_clean()
        test_model.save(using=self._db)

        return test_model


class TestModel(BaseModel):
    class Variants(models.TextChoices):  # type: ignore[misc,name-defined]
        FIRST = "FIRST"
        SECOND = "SECOND"
        THIRD = "THIRD"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    char_field = models.CharField(max_length=256, null=True, blank=True)
    second_char_field = models.CharField(max_length=256, null=True, blank=True)
    char_field_with_choices = models.CharField(max_length=256, choices=Variants.choices, null=True, blank=True)
    integer_field = models.IntegerField(null=True, blank=True)

    objects = TestModelManager()  # type: ignore[assignment]
