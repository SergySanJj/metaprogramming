from functools import wraps


def typecheck(f):
    @wraps(f)
    def g(cls, val):
        if cls.python_type is None:
            raise Exception('python_type not specified')
        if not isinstance(val, cls.python_type):
            raise ValueError(f'Expected type {cls.python_type.__name__}, '
                             f'got {val} of type {val.__class__.__name__}')
        return f(cls, val)

    return g
