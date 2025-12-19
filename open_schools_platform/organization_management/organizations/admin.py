from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path

from open_schools_platform.common.admin import InputFilter, BaseAdmin, admin_wrapper
from open_schools_platform.marketplace_management.models import Installation
from open_schools_platform.organization_management.organizations.models import Organization
from django.utils.translation import gettext_lazy as _

from open_schools_platform.organization_management.organizations.selectors import get_organizations


class INNFilter(InputFilter):
    parameter_name = 'inn'
    title = _('INN')

    def queryset(self, request, queryset):
        if self.value() is not None:
            inn = self.value()

            return get_organizations(filters={"inn": inn})


@admin_wrapper(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ("inn", "id")
    search_fields = ("name",)
    list_filter = (INNFilter,)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<uuid:organization_id>/installations",
                 self.admin_site.admin_view(self.installations_view),
                 name="organization-installations")
        ]

        return custom_urls + urls

    def installations_view(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)
        installations = Installation.objects.filter(organization=organization)

        context = dict(
            self.admin_site.each_context(request),
            title=f"Installations for {organization.name}",
            organization=organization,
            installations=installations,
        )

        #  STUB
        #  Uncomment and specify the path to the template

        # return TemplateResponse(
        #     request,
        #     "admin/organizations/organization/installations.html",
        #     context
        # )
        return HttpResponse(context["installations"])
