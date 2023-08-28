from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.testing.filters import TestModelFilter
from open_schools_platform.testing.models import TestModel


@selector_factory(TestModel)
def get_test_model_objects(*, filters=None, prefetch_related_list=None) -> TestModel:
    filters = filters or {}

    qs = TestModel.objects.all()
    test_model = TestModelFilter(filters, qs).qs

    return test_model
