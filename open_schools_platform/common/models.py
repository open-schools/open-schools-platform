from django.db import models
from django.utils import timezone
from rules.contrib.models import RulesModelMixin, RulesModelBase


class BaseModel(RulesModelMixin, models.Model, metaclass=RulesModelBase):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
