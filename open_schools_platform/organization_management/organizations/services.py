from open_schools_platform.organization_management.organizations.models import Organization


def create_organization(name: str, inn: str) -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization
