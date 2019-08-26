# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class CreateReferenceError(Exception):
    # A run time error, caused by attempts to strongly-type something
    # where we can't make gaurantees. Should not be thrown in python-esc programming
    pass

class DataIntegrityError(Exception):
    # This error is fatal. Our data model doens't match the data
    pass

class Type(object):
    def __init__(self, is_const=False):
        self.is_const = is_const

    def is_copyable_from(self, other):
        return not self.is_const and self.is_initializable_from(other)

class IntegerType(Type):
    def is_initializable_from(self, other):
        return isinstance(other, IntegerType)

class BooleanType(Type):
    def is_initializable_from(self, other):
        return isinstance(other, BooleanType)

class AnyType(Type):
    def is_initializable_from(self, other):
        return True

class ObjectType(Type):
    def __init__(self, property_types, *args, **kwargs):
        super(ObjectType, self).__init__(*args, **kwargs)
        # { foo: IntegerType, bar: StringType ...}
        self.property_types = property_types 

    def is_initializable_from(self, other):
        if not isinstance(other, ObjectType):
            return False
        # At compile time, each property on my version must be *exactly* the same as the other party, because:
        # 1. If either of us has a broader type than the other, they could, later, break the reference
        # 2. There might be extra properties on the object at run time, and we shouldn't assume anything about them
        for our_property_name, our_property_type in self.property_types.items():
            other_property_type = other.property_types.get(our_property_name, MISSING)
            if other_property_type is MISSING:
                return False
            # Stop us from mutating it when we're not allowed
            if other_property_type.is_const and not our_property_type.is_const:
                return False
            # Stop us from mutating later it when the other side has a more specific idea on the type than we do
            if not other_property_type.is_initializable_from(our_property_type) and not our_property_type.is_const:
                return False
            # Stop the other side from mutating it later when we have a more specific idea on the type
            if not our_property_type.is_initializable_from(other_property_type):
                return False
        return True

MISSING = object

class Object(object):
    def __init__(self, properties_and_cells):
        # { foo: Cell(5, IntegerType), bar: Cell("hello", StringType) ...}
        self.properties_and_cells = properties_and_cells
        self.type_references = []

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, ObjectType):
            return False
        # First do value checks - the new reference must accept the current values of the variables
        # This might only be necessary if there are no references to the object yet...
        for new_property_name, new_property_type in new_type_reference.property_types.items():
            our_property_cell = self.properties_and_cells.get(new_property_name, MISSING)
            if our_property_cell is MISSING:
                return False
            if not new_property_type.is_initializable_from(our_property_cell.type):
                return False
        # Then we do the other reference checks. These checks are more liberal than those at compile time, because:
        # 1. We know the type of every reference to the object. These references must be equal or stronger than the compile
        # time checks, and we can be 100% certain we don't break them, which leads to...
        # 2. We can be lenient with properties that aren't bound by others reference checks, because, who cares?
        for other_type_reference in self.type_references:
            common_property_names = list(set(other_type_reference.property_types.keys()) & set(new_type_reference.property_types.keys()))
            # Unlike the compile time checks, we can ignore properties that are not shared by any references
            for common_property_name in common_property_names:
                new_property_type = new_type_reference.property_types[common_property_name]
                other_property_type = other_type_reference.property_types[common_property_name]
                # Stop us from mutating later it when the other side has a more specific idea on the type than we do
                if not other_property_type.is_initializable_from(new_property_type) and not new_property_type.is_const:
                    return False
                # Stop the other side from mutating it later when we have a more specific idea on the type
                if not new_property_type.is_initializable_from(other_property_type) and not other_property_type.is_const:
                    return False
        return True

    def create_reference(self, new_type_reference):
        if self.is_new_type_reference_legal(new_type_reference):
            self.type_references.append(new_type_reference)
        else:
            raise CreateReferenceError()

class Cell(object):
    def __init__(self, value, type):
        if isinstance(type, IntegerType) and not isinstance(value, int):
            raise DataIntegrityError()
        if isinstance(type, BooleanType) and not isinstance(value, bool):
            raise DataIntegrityError()
        if isinstance(type, ObjectType) and not value.is_new_type_reference_legal(type):
            raise DataIntegrityError()

        self.value = value
        self.type = type
