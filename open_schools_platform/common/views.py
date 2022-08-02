from typing import Type, Dict, Union, List, Any

from django.views import View
from rest_framework.fields import ChoiceField, Field
from rest_framework.serializers import Serializer as RestFrameworkSerializer

from open_schools_platform.common.types import DjangoViewType


def MultipleViewManager(handlers: Dict[str, Type[DjangoViewType]]) -> Type[DjangoViewType]:
    method_names = list(map(lambda x: x[0], handlers.items()))

    if not set(method_names).issubset(set(View.http_method_names)):
        raise Exception('Define correct type of requests: ', str(View.http_method_names))

    class BaseManageView(*list(handlers.values())):  # type: ignore
        views_by_method = handlers
        http_method_names = method_names
        """
        The base class for ManageViews
            A ManageView is a view which is used to dispatch the requests to the appropriate views
            This is done so that we can use one URL with different methods (GET, PUT, etc)
        """

        def dispatch(self, request, *args, **kwargs):
            if request.method in self.views_by_method:
                return self.views_by_method[request.method].as_view()(request, *args, **kwargs)
            return super().dispatch(request, *args, **kwargs)

    return BaseManageView


def swagger_dict_response(dict: Dict[str, Union[RestFrameworkSerializer, List[str]]]) -> Type[RestFrameworkSerializer]:
    class Serializer(RestFrameworkSerializer):  # type: ignore
        pass

    fields = {}  # type: Dict[str, Field[Any, Any, Any, Any]]

    for key, value in dict.items():
        if isinstance(value, list):
            fields[key] = ChoiceField(value)
        else:
            fields[key] = value

    Serializer._declared_fields = fields
    return Serializer
