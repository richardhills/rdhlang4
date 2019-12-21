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

def default(value, marker, defaultIfMarker):
    if value is marker:
        return defaultIfMarker
    return value

class RecursiveEntryPoint(object):
    def __init__(self, thread_local):
        self.thread_local = thread_local

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                self.thread_local.values = {}
                #self.thread_local.inside_entry_point = True
                result = func(*args, **kwargs)
                return result
            finally:
                self.thread_local.values = None
        return wrapped

class RecursiveHelper(object):
    def __init__(self, nested_value_factory, thread_local, on_value_callback=None):
        self.nested_value_factory = nested_value_factory
        self.thread_local = thread_local
        self.on_value_callback = on_value_callback

    def __call__(self, func):
        @wraps(func)
        def wrapped(target, *args, **kwargs):
            if not hasattr(self.thread_local, "values"):
                self.thread_local.values = {}

            values = self.thread_local.values

            target_id = id(target)

            if target_id not in values:
                target_value = self.nested_value_factory(target)
                try:
                    values[target_id] = target_value
                    final_value = func(target, *args, **kwargs)
                finally:
                    if not getattr(self.thread_local, "inside_entry_point", False):
                        del values[target_id]
                    else:
                        values[target_id] = final_value
                if self.on_value_callback:
                    self.on_value_callback(target_value, final_value)
                return final_value
            else:
                return values[target_id]
        return wrapped

MISSING = InternalMarker("MISSING")

NO_VALUE = InternalMarker("NO_VALUE")
