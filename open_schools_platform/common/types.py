from typing import TypeVar
from django.db import models
from django.views.generic.base import View

from open_schools_platform.common.models import BaseManager, BaseModel

# Generic type for a Django model
# Reference: https://mypy.readthedocs.io/en/stable/kinds_of_types.html#the-type-of-class-objects

DjangoModelType = TypeVar('DjangoModelType', bound=models.Model)
DjangoViewType = TypeVar('DjangoViewType', bound=View)
