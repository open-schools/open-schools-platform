from open_schools_platform.testing.services import create_test_model


def create_test_model_objects(data_list: list[dict]):
    return list(map(lambda payload: create_test_model(**payload), data_list))
