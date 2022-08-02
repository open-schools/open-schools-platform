from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.services import create_employee
from open_schools_platform.user_management.users.models import User


def create_test_employee(user: User) -> Employee:
    employee = create_employee(name="test_employee", position="test")
    employee.employee_profile = user.employee_profile
    employee.save()
    return employee
