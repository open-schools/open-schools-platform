from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.parent_management.families.models import Family


class FamilyFilter(BaseFilterSet):
    class Meta:
        model = Family
        fields = ('id', 'name')
