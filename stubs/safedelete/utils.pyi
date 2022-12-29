from itertools import chain


def related_objects(obj, only_deleted_by_cascade: bool = ...) -> chain: ...


def can_hard_delete(obj) -> bool: ...
