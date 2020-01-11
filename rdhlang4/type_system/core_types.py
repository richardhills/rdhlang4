# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import threading

from rdhlang4.exception_types import DataIntegrityError, CrystalValueCanNotBeGenerated, \
    InvalidDereferenceError
from rdhlang4.utils import MISSING, InternalMarker, default


def are_bindable(first, second, first_is_rev_const, second_is_rev_const, result_cache):
    """
    Returns True if a name of type self and another name of type other can be bound together.

    Two names can't be bound if a mutation by either party, within the constraints of that
    party, would invalidate the constraints of the other party. Therefore, it is a symmetrical
    test. foo.is_bindable_to(bar) = bar.is_bindable_to(foo).

    This is highly related to copyability. A type X can be copied to type Y as long as the 
    shallow constraints on Y are broader than those on X, and the deeper constraints on Y
    are equal to X.
    """
    if result_cache is None:
        result_cache = {}

    if not isinstance(first, Type):
        raise DataIntegrityError()
    if not isinstance(second, Type):
        raise DataIntegrityError()

    if first is second:
        return True

    first_might_change = not first.is_const
    okay_for_second_to_be_changed_by_first = second_is_rev_const

    if first_might_change and not okay_for_second_to_be_changed_by_first:
        if not second.is_copyable_from(first, result_cache):
            return False

    second_might_change = not second.is_const
    okay_for_first_to_be_changed_by_second = first_is_rev_const

    if second_might_change and not okay_for_first_to_be_changed_by_second:
        if not first.is_copyable_from(second, result_cache):
            return False

    return True

def are_break_types_equal(first, second):
    for break_mode in set(list(first.keys()) + list(second.keys())):
        first_break_type = first.get(break_mode, MISSING)
        second_break_type = second.get(break_mode, MISSING)

        if first_break_type is MISSING or second_break_type is MISSING:
            return False

        if not are_bindable(first_break_type, second_break_type, False, False, {}):
            return False

    return True

class Type(object):

    def __init__(self, is_const=False):
        self.is_const = is_const

    def is_copyable_from(self, other, result_cache):
        raise NotImplementedError(self)

    def replace_inferred_types(self, other):
        return self

    def get_crystal_value(self):
        raise CrystalValueCanNotBeGenerated(self)

    def visit(self, visitor, key=None, obj=None):
        enter_result = visitor.enter(self, key=key, obj=obj)
        new_type = None
        if CREATE_NEW_TYPE in enter_result:
            new_type = self
        result = visitor.exit(original_type=self, new_type=new_type, key=key, obj=obj)
        if result is None:
            raise ValueError()
        return result

    def __repr__(self):
        return type_repr(self)

VISIT_CHILDREN = InternalMarker("VISIT_CHILDREN")
CREATE_NEW_TYPE = InternalMarker("CREATE_NEW_TYPE")

class StringType(Type):

    def is_copyable_from(self, other, result_cache):
        if isinstance(other, StringType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, str):
            return True
        return False

    def to_dict(self):
        return {
            "type": "String"
        }

    def __repr__(self):
        return "StringType"


class IntegerType(Type):

    def is_copyable_from(self, other, result_cache):
        if isinstance(other, IntegerType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, int):
            return True
        if isinstance(other, OneOfType) and all([self.is_copyable_from(s, result_cache) for s in other.types]):
            return True
        return False

    def to_dict(self):
        return {
            "type": "Integer"
        }

    def __repr__(self):
        return "IntegerType"


class BooleanType(Type):

    def is_copyable_from(self, other, result_cache):
        if isinstance(other, BooleanType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, bool):
            return True
        return False

    def to_dict(self):
        return {
            "type": "Boolean"
        }

    def __repr__(self):
        return "BooleanType"


class AnyType(Type):

    def is_copyable_from(self, other, result_cache):
        return not isinstance(other, NoValueType)

    def to_dict(self):
        return {
            "type": "Any"
        }

    def __repr__(self):
        return "AnyType"

def broaden_inferred_type(type):
    if isinstance(type, UnitType):
        if isinstance(type.value, int):
            return IntegerType()
        if isinstance(type.value, str):
            return StringType()
        if isinstance(type.value, bool):
            return BooleanType()
    return type

def safe_get_crystal_value(type):
    try:
        return type.get_crystal_value()
    except CrystalValueCanNotBeGenerated:
        return MISSING

class InferredType(Type):
    def is_copyable_from(self, other, result_cache):
        raise DataIntegrityError()

    def replace_inferred_types(self, other):
        return broaden_inferred_type(other)

    def to_dict(self):
        return {
            "type": "Inferred"
        }

    def __repr__(self):
        return "InferredType"

class NoType(Type):
    def is_copyable_from(self, other, result_cache):
        return isinstance(other, NoType)

    def to_dict(self):
        return {
            "type": "NoType"
        }

    def __repr__(self):
        return "NoType"

class NoValueType(Type):

    def is_copyable_from(self, other, result_cache):
        return isinstance(other, NoValueType)

    def to_dict(self):
        return {
            "type": "NoValueType"
        }

    def __repr__(self):
        return "NoValueType"

class UnitType(Type):

    def __init__(self, value, *args, **kwargs):
        super(UnitType, self).__init__(*args, **kwargs)
        self.value = value

    def is_copyable_from(self, other, result_cache):
        return isinstance(other, UnitType) and other.value == self.value

    def get_crystal_value(self):
        return self.value

    def to_dict(self):
        return {
            "type": "Unit",
            "value": self.value
        }

    def __repr__(self):
        if isinstance(self.value, str):
            return "UnitType<\"{}\">".format(self.value)
        else:
            return "UnitType<{}>".format(self.value)

class UnknownType(Type):
    def is_copyable_from(self, other, result_cache):
        return False

    def to_dict(self):
        return {
            "type": "Unknown"
        }

    def __repr__(self):
        return "Unknown"

def flatten_types(types):
    result = []
    for type in types:
        if isinstance(type, OneOfType):
            result.extend(flatten_types(type.types))
        else:
            result.append(type)
    return result

def dedupe_types(types):
    types_to_drop = list()
    types_to_keep = list()

    if len(types) == 1:
        return types

    types_without_revconst = [t.visit(RemoveRevConst()) for t in types]

    result_cache = {}

    for i1, (tr1, t1) in enumerate(zip(types, types_without_revconst)):
        for i2, (tr2, t2) in enumerate(zip(types, types_without_revconst)):
            if i1 == i2:
                continue
            if t1.is_copyable_from(tr2, result_cache):
                types_to_drop.append(tr2)
                if i1 > i2 and t2.is_copyable_from(tr1, result_cache):
                    types_to_keep.append(tr2)

    return [ t for t in types if t not in types_to_drop ] + types_to_keep

def merge_types(types):
    types = dedupe_types(flatten_types(types))
    types = [t for t in types if not isinstance(t, NoType)]
    if len(types) == 0:
        return NoValueType()
    elif len(types) == 1:
        return types[0]
    else:
        return OneOfType(types)


class OneOfType(Type):

    def __init__(self, types, *args, **kwargs):
        super(OneOfType, self).__init__(*args, **kwargs)
        self.types = types

    def is_copyable_from(self, other, result_cache):
        if self is other:
            return True

        types_that_need_checking = [ other ]
        if isinstance(other, OneOfType):
            types_that_need_checking = other.types
        for other_type in types_that_need_checking:
            for our_type in self.types:
                if our_type.is_copyable_from(other_type, result_cache):
                    break
            else:
                return False
        return True

    def to_dict(self):
        return {
            "type": "OneOfType",
            "types": [t.to_dict() for t in self.types]
        }

    def visit(self, visitor, key=None, obj=None):
        visitor_value = visitor.enter(self, key)

        if VISIT_CHILDREN in visitor_value:
            new_types = [old_type.visit(visitor) for old_type in self.types]
        else:
            new_types = self.types

        new_type = None
        if CREATE_NEW_TYPE in visitor_value:
            new_type = merge_types(new_types)

        return visitor.exit(original_type=self, new_type=new_type, key=key, obj=obj)

    def __repr__(self):
        return "OneOfType<{}>".format(", ".join(repr(t) for t in self.types))

def compare_composite_types(first, second, first_subset_of_second, second_subset_of_first, result_cache):
    if type(first) != type(second):
        return False

    if first is second:
        return True

    first_id = id(first)
    second_id = id(second)
    result_lookup = (first_id, second_id)

    cached_result = result_cache.get(result_lookup, MISSING)
    if cached_result is not MISSING:
        return cached_result

    result_cache[result_lookup] = True
    result_cache[result_lookup] = uncached_compare_composite_types(first, second, first_subset_of_second, second_subset_of_first, result_cache)
    return result_cache[result_lookup]

def uncached_compare_composite_types(first, second, first_subset_of_second, second_subset_of_first, result_cache):
    first_keys = set(first.get_keys())
    second_keys = set(second.get_keys())

    only_in_first = first_keys - second_keys
    only_in_second = second_keys - first_keys
    in_both = first_keys & second_keys

    if first_subset_of_second and len(only_in_first) > 0:
        return False
    if second_subset_of_first and len(only_in_second) > 0:
        return False

    for key_in_both in in_both:
        first_key_type, _ = first.get_key_type(key_in_both)
        second_key_type, _ = second.get_key_type(key_in_both)

        if not are_bindable(
            first_key_type,
            second_key_type,
            first.is_rev_const,
            second.is_rev_const,
            result_cache
        ):
            return False

    if not isinstance(first.wildcard_type, NoType):
        for second_key in only_in_second:
            second_key_type, _ = second.get_key_type(second_key)
            if not are_bindable(
                first.wildcard_type,
                second_key_type,
                first.is_rev_const,
                second.is_rev_const,
                result_cache
            ):
                return False

    if not isinstance(second.wildcard_type, NoType):
        for first_key in only_in_first:
            first_key_type, _ = first.get_key_type(first_key)
            if not are_bindable(
                first_key_type,
                second.wildcard_type,
                first.is_rev_const,
                second.is_rev_const,
                result_cache
            ):
                return False

    if not isinstance(first.wildcard_type, NoType) and not isinstance(second.wildcard_type, NoType):
        if not are_bindable(
            first.wildcard_type,
            second.wildcard_type,
            first.is_rev_const,
            second.is_rev_const,
            result_cache
        ):
            return False

    return True

class CompositeType(Type):
    def get_keys(self):
        raise NotImplementedError()

    def get_key_type(self, key):
        raise NotImplementedError()

    def get_keys_and_types(self):
        raise NotImplementedError()

    def is_copyable_from(self, other, result_cache):
        return compare_composite_types(self, other, True, False, result_cache)

class ObjectType(CompositeType):
    wildcard_type = NoType()

    def __init__(self, property_types, is_rev_const, *args, **kwargs):
        super(ObjectType, self).__init__(*args, **kwargs)
        # { foo: IntegerType, bar: StringType ...}
        self._property_types = dict(property_types)
        self.is_rev_const = is_rev_const
        for property_name, property_type in self._property_types.items():
            if not isinstance(property_name, str):
                raise DataIntegrityError("property_name {} is type {} and not str".format(str(property_name), type(property_name)))
            if not isinstance(property_type, Type):
                raise DataIntegrityError("property_type {} is type {} and not a Type".format(str(property_type), type(property_type)))

    def get_keys(self):
        return self.property_types

    def get_key_type(self, key):
        if not isinstance(key, str):
            raise InvalidDereferenceError()
        key_type = self.property_types.get(key, MISSING)
        if key_type is not MISSING:
            return key_type, False
        else:
            return self.wildcard_type, True

    def get_keys_and_types(self):
        return self.property_types.items()

    @property
    def property_types(self):
        return self._property_types

    def visit(self, visitor, key=None, obj=None):
        enter_value = visitor.enter(self, key=key, obj=obj)

        if VISIT_CHILDREN in enter_value:
            new_property_types = {
                property_name: property_type.visit(visitor, key=property_name, obj=self)
                for property_name, property_type in self.property_types.items()
            }
        else:
            new_property_types = self.property_types

        new_type = None

        if CREATE_NEW_TYPE in enter_value:
            new_type = ObjectType(new_property_types, self.is_rev_const)

        return visitor.exit(original_type=self, new_type=new_type, key=key, obj=obj)

    def replace_inferred_types(self, other):
        if not isinstance(other, ObjectType):
            return self
        return ObjectType({
            property_name: property_type.replace_inferred_types(other.property_types[property_name])
            for property_name, property_type in self.property_types.items()
        }, False)

    def get_crystal_value(self):
        from rdhlang4.type_system.values import Object
        return Object({
            property_name: property_type.get_crystal_value() for property_name, property_type in self.property_types.items()
        })

    def to_dict(self):
        return {
            "type": "Object",
            "properties": {
                name: value.to_dict() for name, value in self.property_types.items()
            }
        }

def type_repr(type):
    visitor = TypeRepr()
    type.visit(visitor)
    return visitor.result

class TypeRepr(object):
    def __init__(self):
        self.result = ""
        self.already_seen = set()
        self.indent = 0

    def enter(self, type, key=None, obj=None):
        self.result += "  " * self.indent
        if key:
            self.result += (key + ": ")

        if isinstance(type, ObjectType):
            self.result += "ObjectType<"

            if id(type) in self.already_seen:
                self.result += "..."
                return ()
            else:
                if type.is_rev_const:
                    self.result += "R"
                if type.is_const:
                    self.result += "C"
                self.result += "\n"
                self.indent += 1
                self.already_seen.add(id(type))
                return (VISIT_CHILDREN,)
        else:
            self.result += repr(type)
            self.result += "\n"
            return (VISIT_CHILDREN,)

    def exit(self, original_type=None, new_type=None, key=None, obj=None):
        if isinstance(original_type, ObjectType):
            self.indent -= 1
            self.result += "  " * self.indent
            self.result += ">\n"
        return original_type

class RemoveRevConst(object):
    def __init__(self):
        self.already_entered = set()
        self.results = dict()

    def enter(self, type, key=None, obj=None):
        if id(type) in self.already_entered:
            return (CREATE_NEW_TYPE,)
        else:
            self.already_entered.add(id(type))
            return (CREATE_NEW_TYPE, VISIT_CHILDREN)

    def exit(self, original_type=None, new_type=None, key=None, obj=None):
        if id(original_type) not in self.results:
            if isinstance(new_type, (ObjectType, ListType)) and new_type.is_rev_const:
                new_type.is_rev_const = False
            self.results[id(original_type)] = new_type

        return self.results[id(original_type)]

class ListType(CompositeType):
    def __init__(self, entry_types, wildcard_type, is_rev_const, *args, **kwargs):
        super(ListType, self).__init__(*args, **kwargs)
        # [ IntegerType, StringType ... ]
        self.entry_types = list(entry_types)
        self.wildcard_type = wildcard_type
        self.is_rev_const = is_rev_const

        for property_type in self.entry_types:
            if not isinstance(property_type, Type):
                raise DataIntegrityError()
        if not isinstance(self.wildcard_type, Type):
            raise DataIntegrityError()

    def get_keys(self):
        return list(range(len(self.entry_types)))

    def get_key_type(self, key):
        if not isinstance(key, int):
            raise InvalidDereferenceError()
        if key >= 0 and key < len(self.entry_types):
            return self.entry_types[key], False
        else:
            return self.wildcard_type, True

    def get_keys_and_types(self):
        return list(enumerate(self.entry_types))

    def visit(self, visitor, key=None, obj=None):
        enter_value = visitor.enter(self, key=key, obj=obj)

        if VISIT_CHILDREN in enter_value:
            new_entry_types = [
                entry_type.visit(visitor, key=index, obj=self)
                for index, entry_type in enumerate(self.entry_types)
            ]
            new_wildcard_type = self.wildcard_type.visit(visitor)
        else:
            new_entry_types = self.entry_types
            new_wildcard_type = self.wildcard_type

        new_type = None

        if CREATE_NEW_TYPE in enter_value:
            new_type = ListType(new_entry_types, new_wildcard_type, self.is_rev_const)

        return visitor.exit(original_type=self, new_type=new_type, key=key, obj=obj)

    def get_crystal_value(self):
        from rdhlang4.type_system.values import List
        return List([p.get_crystal_value() for p in self.entry_types])

class FunctionType(Type):

    def __init__(self, argument_type, break_types, *args, **kwargs):
        super(FunctionType, self).__init__(*args, **kwargs)
        self.argument_type = argument_type
        self.break_types = break_types

    def is_copyable_from(self, other, result_cache):
        if self is other:
            return True

        if not isinstance(other, FunctionType):
            return False

        if not other.argument_type.is_copyable_from(self.argument_type, result_cache):
            return False

        for break_mode, other_break_type in other.break_types.items():
            our_break_type = self.break_types.get(break_mode, MISSING)
            if our_break_type is MISSING:
                return False
            if not our_break_type.is_copyable_from(other_break_type, result_cache):
                return False

        return True

    def to_dict(self):
        return {
            "type": "Function",
            "argument": self.argument_type.to_dict(),
            "breaks": {
                mode: type.to_dict() for (mode, type) in self.break_types.items()
            }
        }

    def __repr__(self):
        return "Function<{} => {}>".format(self.argument_type, self.break_types)

class PythonFunction(Type):
    def __init__(self, func, *args, **kwargs):
        super(PythonFunction, self).__init__(*args, **kwargs)
        self.func = func

    def is_copyable_from(self, other, result_cache):
        return isinstance(other, PythonFunction)

    def __repr__(self):
        return "PythonFunction<{}>".format(self.func)
