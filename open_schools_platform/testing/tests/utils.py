from open_schools_platform.testing.services import create_test_model


def create_test_model_objects(data_list: list[dict]):
    objects = []

    for payload in data_list:
        model_object = create_test_model(**payload)
        objects.append(model_object)

    return objects
