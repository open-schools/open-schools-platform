from typing import Any, Tuple, Optional, Type, Union  # noqa: F401
from safedelete.queryset import SafeDeleteQueryset  # noqa: F401
import safedelete
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone
from rules.contrib.models import RulesModelMixin, RulesModelBase
from safedelete.config import FIELD_NAME
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel


class BaseManager(SafeDeleteManager):
    def update_or_create_with_check(self, defaults=None, password: str = None, **kwargs) -> models.Model:
        """See :func:`~django.db.models.Query.update_or_create.`.

        Change to regular djangoesk function:
        Regular update_or_create() fails on soft-deleted, existing record with unique constraint on non-id field
        If object is soft-deleted we don't update-or-create it but reset the deleted field to None.
        So the object is visible again like a create in any other case.

        Attention: If the object is "revived" from a soft-deleted state the created return value will
        still be false because the object is technically not created unless you set

        Args:
            defaults: Dict with defaults to update/create model instance with
            password: For AbstractBaseUser models
            kwargs: Attributes to lookup model instance with
        """

        # Check if one of the model fields contains a unique constraint
        if self.model.has_unique_fields() or 'pk' in kwargs or self.model._meta.pk.name in kwargs:
            # Check if object is already soft-deleted
            deleted_object = self.all_with_deleted().filter(**kwargs).exclude(**{FIELD_NAME: None}).first()

            # If object is soft-deleted, reset delete-state...
            if deleted_object and deleted_object._safedelete_policy in self.get_soft_delete_policies():
                setattr(deleted_object, FIELD_NAME, None)
                deleted_object.save()

        params = dict(kwargs, **defaults)
        try:
            obj = self.get_queryset().get(**kwargs)
            from open_schools_platform.common.services import model_update
            model_update(instance=obj, fields=list(defaults.keys()), data=params)
        except self.model.DoesNotExist:
            obj = self.model(**params)

        if isinstance(obj, AbstractBaseUser):
            if password:
                obj.set_password(password)
            else:
                obj.set_unusable_password()
        obj.full_clean()
        obj.save(using=self.db)
        return obj


class BaseModel(RulesModelMixin, SafeDeleteModel, metaclass=RulesModelBase):
    _safedelete_policy = safedelete.config.SOFT_DELETE_CASCADE
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
