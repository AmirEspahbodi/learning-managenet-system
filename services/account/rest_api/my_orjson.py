import functools
import orjson


def strict_constant(o):
    raise ValueError("Out of range float values are not JSON compliant: " + repr(o))


@functools.wraps(orjson.dumps)
def dumps(*args, **kwargs):
    kwargs.setdefault("allow_nan", False)
    return orjson.dumps(*args, **kwargs)


@functools.wraps(orjson.loads)
def loads(*args, **kwargs):
    kwargs.setdefault("parse_constant", strict_constant)
    return orjson.loads(*args, **kwargs)
