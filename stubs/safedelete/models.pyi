from django.db import models
from typing import Any, Dict, Optional, Tuple, Iterable, Type

from safedelete.managers import SafeDeleteAllManager, SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.queryset import SafeDeleteQueryset


def is_safedelete_cls(cls): ...


def is_safedelete(related): ...


class SafeDeleteModel(models.Model):
    objects: Type[SafeDeleteManager]  # type: ignore[assignment]
    all_objects: SafeDeleteAllManager
    deleted_objects: SafeDeleteDeletedManager

    class Meta:
        abstract: bool

    def save(self, keep_deleted: bool = ...,  # type: ignore[override]
             *,
             force_insert: bool = False,
             force_update: bool = False,
             using: Optional[str] = None,
             update_fields: Optional[Iterable[str]] = None) -> None: ...

    def undelete(self, force_policy: Optional[int] = ..., **kwargs) -> Tuple[int, Dict[str, int]]: ...

    def delete(self, force_policy: Any | None = ..., *,  # type: ignore[override]
               using: Any = None,
               keep_parents: bool = False) -> tuple[int, dict[str, int]]: ...

    def soft_delete_policy_action(self, **kwargs) -> Tuple[int, Dict[str, int]]: ...

    def hard_delete_policy_action(self, **kwargs) -> Tuple[int, Dict[str, int]]: ...

    def hard_delete_cascade_policy_action(self, **kwargs) -> Tuple[int, Dict[str, int]]: ...

    def soft_delete_cascade_policy_action(self, **kwargs) -> Tuple[int, Dict[str, int]]: ...

    @classmethod
    def has_unique_fields(cls) -> bool: ...


class SafeDeleteMixin(SafeDeleteModel):
    class Meta:
        abstract: bool

    def __init__(self, *args, **kwargs) -> None: ...
