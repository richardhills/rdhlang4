from functools import wraps

def spread_dict(*args, **kwargs):
    result = {}
    for arg in args:
        result.update(arg)
    result.update(kwargs)
    return result


class InternalMarker(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

def default(value, marker, default_if_marker):
    if value is marker:
        return default_if_marker
    return value

MISSING = InternalMarker("MISSING")

NO_VALUE = InternalMarker("NO_VALUE")
