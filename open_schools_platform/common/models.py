import safedelete
from django.db import models
from django.utils import timezone
from rules.contrib.models import RulesModelMixin, RulesModelBase
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel


class BaseManager(SafeDeleteManager):
    def update_or_create(self, defaults=None, **kwargs):
        super().update_or_create(defaults=defaults, **kwargs)


class BaseModel(RulesModelMixin, SafeDeleteModel, metaclass=RulesModelBase):
    _safedelete_policy = safedelete.config.NO_DELETE
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
