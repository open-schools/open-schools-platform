from typing import Any, Dict, List

from open_schools_platform.organization_management.employees.services import create_employee

from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.services import create_user


def create_test_users():
    data_user_list = [
        {
            "phone": "+79999999901",
            "password": "123456",
            "name": "Andrey"
        },
        {
            "phone": "+79999999902",
            "password": "123456",
            "name": "Alexander"
        },
    ]

    users = []

    for data in data_user_list:
        user = create_user(**data)
        users.append(user)

    return users


def create_test_employees(users: List[User], organizations: List[Organization]):
    data_employee_list = [
        {
            "name": "Andrey",
            "position": "Chief director",
            "user": users[0],
            "organization": organizations[0]
        },
        {
            "name": "Alexander",
            "position": "Chief cleaner",
            "user": users[1],
            "organization": organizations[0]
        },
    ]  # type: List[Dict[str, Any]]

    employees = []

    for data in data_employee_list:
        employee = create_employee(**data)
        employees.append(employee)

    return employees


def create_test_organizations():
    data_organization_list = [
        {
            "name": "LamArt",
            "inn": "1"
        },
        {
            "name": "LamaBox",
            "inn": "1"
        },
    ]

    organizations = []

    for data in data_organization_list:
        organization = create_organization(**data)
        organizations.append(organization)

    return organizations


def create_test_employee(user: User, organization: Organization = None):
    return create_employee(name="test_employee", position="test", user=user, organization=organization)
