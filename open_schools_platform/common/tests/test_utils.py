from json import loads

key_transform = {"id": str}


class GetRequestTesting:
    '''
    creation_count calls creation_function once, which generates data in the database. arguments of creation_function:
    i - the number of the current data entity and the remaining arguments: creation_function_args (dictionary)

    example:
    create_test_family(i, parent):
        return create_family(parent=parent, name=f"test_family{i}")
    '''

    @staticmethod
    def create_testdata_in_db(creation_count, creation_function,
                              creation_function_args=None):
        id_list = []

        for i in range(creation_count):
            creation_object = creation_function(i, **creation_function_args)
            id = str(creation_object.id)
            id_list.append(id)
        id_list.sort()
        return id_list

    @staticmethod
    def get_results(response):
        data = [item["id"] for item in loads(response.content.decode())["results"]]
        data.sort()
        return data
