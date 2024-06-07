from inspect import signature, Parameter
from typing import Tuple


def predicate_input_type_check(function):
    def wrapper(*args, **kwargs):
        sig = signature(function)
        param_list: list[Tuple[str, Parameter]] = list(sig.parameters.items())
        if len(param_list) < len(args) + len(kwargs):
            return False

        for i in range(len(args)):
            if not isinstance(args[i], param_list[i][1].annotation):
                return False

        for kwarg in kwargs.items():
            if type(kwarg[1]) != sig.parameters[kwarg[0]]:
                return False
        return function(*args, **kwargs)

    return wrapper
