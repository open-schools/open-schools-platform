from open_schools_platform.common.filters import BaseFilterSet
from django_filters import DateFilter


class HistoryFilter(BaseFilterSet):
    begin_date = DateFilter()
    end_date = DateFilter()
