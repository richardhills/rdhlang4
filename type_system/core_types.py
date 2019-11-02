# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from __builtin__ import False

from bunch import Bunch

from exception_types import DataIntegrityError, IncompatableAssignmentError, \
    CreateReferenceError, FatalException
from utils import InternalMarker, MISSING, NO_VALUE
from prompt_toolkit.key_binding.bindings.named_commands import self_insert

class Type(object):

    def __init__(self, is_const=False, is_rev_const=False):
        self.is_const = is_const
        self.is_rev_const = is_rev_const

    def is_bindable_to(self, other):
        """
        Returns True if a name of type self and another name of type other can be bound together.

        Two names can't be bound if a mutation by either party, within the constraints of that
        party, would invalidate the constraints of the other party. Therefore, it is a symmetrical
        test. foo.is_bindable_to(bar) = bar.is_bindable_to(foo).

        This is highly related to copyability. A type X can be copied to type Y as long as the 
        shallow constraints on Y are broader than those on X, and the deeper constraints on Y
        are equal to X.
        """
        if not isinstance(other, Type):
            raise DataIntegrityError()

        if not self.is_const and not other.is_rev_const:
            if not other.is_copyable_from(self):
                return False
        if not other.is_const and not self.is_rev_const:
            if not self.is_copyable_from(other):
                return False
        return True

    def is_copyable_from(self, other):
        raise NotImplementedError()

    def replace_inferred_types(self, other):
        return self

    def get_crystal_value(self):
        raise NotImplementedError(type(self))


class StringType(Type):

    def is_copyable_from(self, other):
        if isinstance(other, StringType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, basestring):
            return True
        return False

    def to_dict(self):
        return {
            "type": "String"
        }

    def __repr__(self):
        return "StringType"


class IntegerType(Type):

    def is_copyable_from(self, other):
        if isinstance(other, IntegerType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, int):
            return True
        if isinstance(other, OneOfType) and all([self.is_copyable_from(s) for s in other.types]):
            return True
        return False

    def to_dict(self):
        return {
            "type": "Integer"
        }

    def __eq__(self, other):
        return isinstance(other, IntegerType)

    def __repr__(self):
        return "IntegerType"


class BooleanType(Type):

    def is_copyable_from(self, other):
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

    def is_copyable_from(self, other):
        return True

    def to_dict(self):
        return {
            "type": "Any"
        }

    def __eq__(self, other):
        return isinstance(other, AnyType)

    def __repr__(self):
        return "AnyType"

def broaden_inferred_type(type):
    if isinstance(type, UnitType):
        if isinstance(type.value, int):
            return IntegerType()
        if isinstance(type.value, basestring):
            return StringType()
        if isinstance(type.value, bool):
            return BooleanType()
    return type

class InferredType(Type):
    def is_copyable_from(self, other):
        return True

    def replace_inferred_types(self, other):
        return broaden_inferred_type(other)

    def to_dict(self):
        return {
            "type": "Inferred"
        }

    def __repr__(self):
        return "InferredType"

class VoidType(Type):

    def is_copyable_from(self, other):
        return isinstance(other, VoidType)

    def to_dict(self):
        return {
            "type": "Void"
        }

    def __repr__(self):
        return "VoidType"


class UnitType(Type):

    def __init__(self, value, *args, **kwargs):
        super(UnitType, self).__init__(*args, **kwargs)
        self.value = value

    def is_copyable_from(self, other):
        return isinstance(other, UnitType) and other.value == self.value

    def get_crystal_value(self):
        return self.value

    def to_dict(self):
        return {
            "type": "Unit",
            "value": self.value
        }

    def __hash__(self, *args, **kwargs):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, UnitType) and other.value == self.value

    def __repr__(self):
        return "UnitType<{}>".format(self.value)

def flatten_types(types):
    result = []
    for type in types:
        if isinstance(type, OneOfType):
            result.extend(type.types)
        else:
            result.append(type)
    return result

def dedupe_types(types):
    types_to_drop = set()
    types_to_keep = set()

    for i1, t1 in enumerate(types):
        for i2, t2 in enumerate(types):
            if t1 is not t2:
                if t1.is_copyable_from(t2):
                    types_to_drop.add(t2)
                if t1.is_bindable_to(t2):
                    types_to_keep.add(t1 if i1 > i2 else t2)

    return list((set(types) - types_to_drop) | types_to_keep)


def merge_types(types):
    types = dedupe_types(flatten_types(types))
    types = [t for t in types if not isinstance(t, VoidType)]
    if len(types) == 0:
        return VoidType()
    elif len(types) == 1:
        return types[0]
    else:
        return OneOfType(types)


class OneOfType(Type):

    def __init__(self, types, *args, **kwargs):
        super(OneOfType, self).__init__(*args, **kwargs)
        self.types = types

    def is_copyable_from(self, other):
        types_that_need_checking = [ other ]
        if isinstance(other, OneOfType):
            types_that_need_checking = other.types
        for other_type in types_that_need_checking:
            for our_type in self.types:
                if our_type.is_copyable_from(other_type):
                    break
            else:
                return False
        return True

    def to_dict(self):
        return {
            "type": "OneOfType",
            "types": [t.to_dict() for t in self.types]
        }

    def __eq__(self, other):
        if not isinstance(other, OneOfType):
            return False
        return set(self.types) == set(other.types)

    def __repr__(self):
        return "OneOfType<{}>".format(", ".join(repr(t) for t in self.types))


class ObjectType(Type):

    def __init__(self, property_types, *args, **kwargs):
        super(ObjectType, self).__init__(*args, **kwargs)
        # { foo: IntegerType, bar: StringType ...}
        self.property_types = dict(property_types)
        for property_name, property_type in self.property_types.items():
            if not isinstance(property_name, basestring) or not isinstance(property_type, Type):
                raise DataIntegrityError()

    def is_copyable_from(self, other):
        if not isinstance(other, ObjectType):
            return False
        # At compile time, each property on my version must be *exactly* the same as the other party, because:
        # 1. If either of us has a broader type than the other, they could, later, break the reference
        # 2. There might be extra properties on the object at run time, and we shouldn't assume anything about them
        for our_property_name, our_property_type in self.property_types.items():
            other_property_type = other.property_types.get(our_property_name, MISSING)
            if other_property_type is MISSING:
                return False

            if not our_property_type.is_bindable_to(other_property_type):
                return False

#             # Stop us from mutating it when we're not allowed
#             if other_property_type.is_const and not our_property_type.is_const:
#                 return False
#             # Stop us from mutating later it when the other side has a more specific idea on the type than we do
#             if not other_property_type.is_bindable_to(our_property_type) and not our_property_type.is_const:
#                 return False
#             # Stop the other side from mutating it later when we have a more specific idea on the type
#             if not our_property_type.is_bindable_to(other_property_type):
#                 return False
        return True

    def replace_inferred_types(self, other):
        if not isinstance(other, ObjectType):
            return self
        return ObjectType({
            property_name: property_type.replace_inferred_types(other.property_types[property_name])
            for property_name, property_type in self.property_types.items()
        })

    def get_crystal_value(self):
        from type_system.values import Object
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

    def __repr__(self, *args, **kwargs):
        return "Object<\n{}\n>".format(",\n".join([
            "  {}: {}".format(property_name, property_type) for property_name, property_type in self.property_types.items()
        ]))

class TupleType(Type):
    def __init__(self, property_types, *args, **kwargs):
        super(TupleType, self).__init__(*args, **kwargs)
        # [ IntegerType, StringType ... ]
        self.property_types = list(property_types)
        for property_type in self.property_types:
            if not isinstance(property_type, Type):
                raise DataIntegrityError()

    def get_crystal_value(self):
        return tuple(p.get_crystal_value() for p in self.property_types)

class FunctionType(Type):

    def __init__(self, argument_type, break_types, *args, **kwargs):
        super(FunctionType, self).__init__(*args, **kwargs)
        self.argument_type = argument_type
        self.break_types = break_types

    def is_copyable_from(self, other):
        if not isinstance(other, FunctionType):
            return False

        if not other.argument_type.is_copyable_from(self.argument_type):
            return False

        for break_mode, other_break_type in other.break_types.items():
            our_break_type = self.break_types.get(break_mode, MISSING)
            if our_break_type is MISSING:
                return False
            if not our_break_type.is_copyable_from(other_break_type):
                return False

        return True

    def __repr__(self):
        return "Function<{} => {}>".format(self.argument_type, self.break_types)

