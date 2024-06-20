from inspect import signature, Parameter
from typing import Tuple

from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.organizations.models import Organization


def predicate_input_type_check(function):
    def wrapper(*args, **kwargs):
        sig = signature(function)
        param_list: list[Tuple[str, Parameter]] = list(sig.parameters.items())
        if len(param_list) < len(args) + len(kwargs):
            return False

        for i in range(len(args)):
            if not isinstance(args[i], param_list[i][1].annotation):
                return False

        for kwarg in kwargs.items():
            if type(kwarg[1]) != sig.parameters[kwarg[0]]:
                return False
        return function(*args, **kwargs)

    return wrapper


def has_related_organization(user, organization):
    employees = Employee.objects.filter(employee_profile=user.employee_profile)
    if not employees:
        return False

    organizations_ids = list(map(lambda e: e.organization.id, employees))
    organizations = Organization.objects.filter(id__in=organizations_ids)
    return organization in organizations
