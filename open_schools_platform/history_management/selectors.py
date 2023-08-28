from open_schools_platform.common.utils import convert_str_date_to_datetime
from rest_framework.exceptions import ValidationError, ErrorDetail


def get_history(model, filters=None):
    filters = filters or {}
    qs = model.history.all()

    begin_date = filters.get('begin_date', None)
    end_date = filters.get('end_date', None)

    if begin_date and end_date:
        begin_datetime = convert_str_date_to_datetime(begin_date, "00:00:00")
        end_datetime = convert_str_date_to_datetime(end_date, "23:59:59")
        if begin_datetime > end_datetime:
            raise ValidationError({'non_field_errors': 'Begin date must be before end date',
                                   'begin_date': ErrorDetail('', code='range_error'),
                                   'end_date': ErrorDetail('', code='range_error')})
        qs = qs.filter(history_date__range=[begin_datetime, end_datetime])

    if begin_date:
        begin_datetime = convert_str_date_to_datetime(begin_date, "00:00:00")
        qs = qs.filter(history_date__gte=begin_datetime)

    if end_date:
        end_datetime = convert_str_date_to_datetime(end_date, "23:59:59")
        qs = qs.filter(history_date__lte=end_datetime)

    return qs
