from functools import wraps
from typing import Type

from .db_type import DBType


def typecheck(f):
    """
    Add type checking for a single argument class function

    :param f: function to decorate
    :return: decorated function
    """

    @wraps(f)
    def g(cls: Type[DBType], val):
        if cls.python_type is None:
            raise Exception('python_type not specified')
        if not isinstance(val, cls.python_type):
            raise ValueError(f'Expected type {cls.python_type.__name__}, '
                             f'got {val} of type {val.__class__.__name__}')
        return f(cls, val)

    return g
