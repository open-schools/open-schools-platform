from .query import SafeDeleteQuery
from django.db import models as models
from django.db.models import query
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union

_QS = TypeVar('_QS', bound='SafeDeleteQueryset')


class SafeDeleteQueryset(query.QuerySet):
    query: Any

    def __init__(self, model: Optional[Type[models.Model]] = ..., query: Optional[SafeDeleteQuery] = ...,
                 using: Optional[str] = ..., hints: Optional[Dict[str, models.Model]] = ...) -> None: ...

    def delete(self, force_policy: Optional[int] = ...) -> Tuple[int, Dict[str, int]]: ...

    def hard_delete_policy_action(self) -> Tuple[int, Dict[str, int]]: ...

    def undelete(self, force_policy: Optional[int] = ...) -> Tuple[int, Dict[str, int]]: ...

    def all(self, force_visibility: Union[Any, None] = ...): ...

    def filter(self, *args, **kwargs): ...
