# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from bunch import Bunch

from utils import InternalMarker, MISSING, NO_VALUE
from pip._vendor.pyparsing import oneOf


class CreateReferenceError(Exception):
    # A run time error, caused by attempts to strongly-type something
    # where we can't make gaurantees. Should only be thrown by casting
    # in strongly typed code
    pass


class IncompatableAssignmentError(Exception):
    # A run time error, caused by attempts in weakly-typed code
    # to assign something to a value that would invalid strongly-syped
    # codes access
    pass


class DataIntegrityError(Exception):
    # This error is fatal. Our data model doesn't match the data
    pass


def infer_primitive_type(value):
    from executor.executor import PreparedFunction

    if isinstance(value, int):
        return IntegerType()
    if isinstance(value, bool):
        return BooleanType()
    if isinstance(value, basestring):
        return StringType()
    if isinstance(value, PreparedFunction):
        return FunctionType(VoidType(), {})
    if isinstance(value, Object):
        return ObjectType({})
    if value is NO_VALUE:
        return VoidType()
    raise DataIntegrityError()


def flatten_to_primitive_type(type):
    if isinstance(type, (BooleanType, IntegerType, StringType, AnyType, VoidType)):
        return type
    if isinstance(type, ObjectType):
        return ObjectType({})
    if isinstance(type, FunctionType):
        return FunctionType(VoidType(), {})
    raise DataIntegrityError("Unknown type {}".format(type))


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

    def get_crystal_value(self):
        return MISSING


class StringType(Type):

    def is_copyable_from(self, other):
        if isinstance(other, StringType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, basestring):
            return True
        return False

    def __repr__(self):
        return "StringType"


class IntegerType(Type):

    def is_copyable_from(self, other):
        if isinstance(other, IntegerType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, int):
            return True
        return False

    def __repr__(self):
        return "IntegerType"


class BooleanType(Type):

    def is_copyable_from(self, other):
        if isinstance(other, BooleanType):
            return True
        if isinstance(other, UnitType) and isinstance(other.value, bool):
            return True
        return False

    def __repr__(self):
        return "BooleanType"


class AnyType(Type):

    def is_copyable_from(self, other):
        return True

    def __repr__(self):
        return "AnyType"


class VoidType(Type):

    def is_copyable_from(self, other):
        return isinstance(other, VoidType)

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
    deduped_types = []
    for index, t1 in enumerate(types):
        for t2 in types[index + 1:]:
            if t1.is_bindable_to(t2):
                break
        else:
            deduped_types.append(t1)
    return deduped_types


def merge_types(types):
    types = dedupe_types(flatten_types(types))
    types = [t for t in types if not isinstance(t, VoidType)]
    if len(types) == 0:
        return VoidType()
    if len(types) == 1:
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

    def get_crystal_value(self):
        return Object({
            property_name: property_type.get_crystal_value() for property_name, property_type in self.property_types.items()
        })

    def __repr__(self, *args, **kwargs):
        return "Object<\n{}\n>".format(",\n".join([
            "  {}: {}".format(property_name, property_type) for property_name, property_type in self.property_types.items()
        ]))


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

class Object(Bunch):
    # Any fields we want to keep out of the bunch dictionary go here
    type_references = None

    def __init__(self, properties_and_values):
        # { foo: Cell(5, IntegerType), bar: Cell("hello", StringType) ...}

#        for value in properties_and_values.values():
#            if value == NO_VALUE:
#                raise DataIntegrityError()

        self.type_references = []
        super(Object, self).__init__(properties_and_values)

    def __setattr__(self, property_name, new_value):
        #if new_value == NO_VALUE:
        #    raise DataIntegrityError()

        if property_name not in [ "type_references" ]:
            for other_type_reference in self.type_references:
                if isinstance(other_type_reference, ObjectType):
                    other_property_type = other_type_reference.property_types.get(property_name, MISSING)
                    if other_property_type is MISSING:
                        continue
                    new_value_primitive_property_type = infer_primitive_type(new_value)
                    other_primitive_property_type = flatten_to_primitive_type(other_property_type)
                    if not other_primitive_property_type.is_copyable_from(new_value_primitive_property_type):
                        raise IncompatableAssignmentError()
    
                    if isinstance(other_primitive_property_type, ObjectType):
                        try:
                            new_value.create_reference(other_property_type)
                        except CreateReferenceError:
                            raise IncompatableAssignmentError()
        Bunch.__setattr__(self, property_name, new_value)

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, ObjectType):
            return False
        # First do value checks - the new reference must accept the current values of the variables
        # This might only be necessary if there are no references to the object yet...
        for new_property_name, new_property_type in new_type_reference.property_types.items():
            our_property_value = self.get(new_property_name, MISSING)
            if our_property_value is MISSING:
                return False
            our_primitive_property_type = infer_primitive_type(our_property_value)
            # Only check for initializability for primitive types, since we'll check reference types later
            new_primitive_property_type = flatten_to_primitive_type(new_property_type)
            if not new_primitive_property_type.is_copyable_from(our_primitive_property_type):
                return False
        # Then we do the other reference checks. These checks are more liberal than those at compile time, because:
        # 1. We know the type of every reference to the object. These references must be equal or stronger than the compile
        # time checks, and we can be 100% certain we don't break them, which leads to...
        # 2. We can be lenient with properties that aren't bound by others reference checks, because, who cares?
        for other_type_reference in self.type_references:
            if isinstance(other_type_reference, ObjectType):
                common_property_names = list(set(other_type_reference.property_types.keys()) & set(new_type_reference.property_types.keys()))
                # Unlike the compile time checks, we can ignore properties that are not shared by any references
                for common_property_name in common_property_names:
                    new_property_type = new_type_reference.property_types[common_property_name]
                    other_property_type = other_type_reference.property_types[common_property_name]
                    # Stop us from mutating later it when the other side has a more specific idea on the type than we do
                    if not other_property_type.is_bindable_to(new_property_type) and not new_property_type.is_const:
                        return False
                    # Stop the other side from mutating it later when we have a more specific idea on the type
                    if not new_property_type.is_bindable_to(other_property_type) and not other_property_type.is_const:
                        return False
        return True

    def create_reference_on_all_child_references(self, new_type_reference):
        if isinstance(new_type_reference, ObjectType):
            for new_property_name, new_property_type in new_type_reference.property_types.items():
                # Identify whether the reference is to an object that also needs constraining with create_reference
                our_property_value = self.get(new_property_name, MISSING)
                if isinstance(our_property_value, Object):
                    our_property_value.create_reference(new_property_type)

    def create_reference(self, new_type_reference):
        if self.is_new_type_reference_legal(new_type_reference):
            self.create_reference_on_all_child_references(new_type_reference)
            self.type_references.append(new_type_reference)
        else:
            raise CreateReferenceError()
