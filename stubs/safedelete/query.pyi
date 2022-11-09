from django.db.models import sql
from django.db.models.sql.compiler import SQLCompiler
from typing import Optional, TypeVar

_Q = TypeVar('_Q', bound='SafeDeleteQuery')


class SafeDeleteQuery(sql.Query):
    def check_field_filter(self, **kwargs) -> None: ...

    def clone(self: SafeDeleteQuery) -> SafeDeleteQuery: ...

    def get_compiler(self, *args, **kwargs) -> SQLCompiler: ...

    def set_limits(self, low: Optional[int] = ..., high: Optional[int] = ...) -> None: ...
