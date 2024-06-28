from operator import attrgetter
from typing import Type, Dict, Union, List, Any

from django.contrib.contenttypes.models import ContentType
from django.views import View
from rest_framework.exceptions import PermissionDenied
from rest_framework.fields import ChoiceField, Field
from rest_framework.serializers import Serializer as RestFrameworkSerializer

from open_schools_platform.common.types import DjangoViewType
from open_schools_platform.organization_management.employees.roles import role_hierarchy


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


def convert_dict_to_serializer(dictionary: Dict[str, Union[RestFrameworkSerializer, List[str]]]) \
        -> Type[RestFrameworkSerializer]:
    class Serializer(RestFrameworkSerializer):  # type: ignore
        pass

    fields = {}  # type: Dict[str, Field[Any, Any, Any, Any]]

    for key, value in dictionary.items():
        if isinstance(value, list):
            fields[key] = ChoiceField(value)
        else:
            fields[key] = value

    Serializer._declared_fields = fields
    return Serializer


def ensure_role_permission(target_model, relation, target_profile, role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args) > 1:
                request = args[1]
                related_entities = {}
                related_entities.update(request.data)
                related_entities.update(request.query_params)
                related_entities.update(request.parser_context.get('kwargs', {}))

                pk = related_entities.get(f'{target_model}_id') or related_entities.get(target_model)
                if pk:
                    target_object = ContentType.objects.get(model=target_model).get_object_for_this_type(pk=pk)
                    retriever = attrgetter(relation)
                    profile = getattr(request.user, target_profile)
                    if profile:
                        relation_object = retriever(target_object).filter(**{target_profile: profile.id}).first()

                        if hasattr(relation_object, 'role'):
                            if relation_object.role in role_hierarchy.get(role, ()):
                                return func(*args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator
