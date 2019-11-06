# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref

from bunch import Bunch

from exception_types import DataIntegrityError, IncompatableAssignmentError, \
    CreateReferenceError
from type_system.core_types import UnitType, ObjectType, VoidType, AnyType, TupleType, are_bindable, \
    are_common_properties_compatible
from utils import NO_VALUE, MISSING


def create_crystal_type(value, set_is_rev_const, mask_type=None):
    from executor.executor import PreparedFunction

    if not isinstance(mask_type, ObjectType):
        mask_type = None

    if isinstance(value, (int, bool, basestring)):
        return UnitType(value)
    if isinstance(value, dict):
        return ObjectType({
            k: create_crystal_type(v, set_is_rev_const, mask_type.property_types[k] if mask_type else None)
                for k, v in value.items() if mask_type is None or k in mask_type.property_types
        }, set_is_rev_const)
    if isinstance(value, list):
        return TupleType([
            create_crystal_type(p, set_is_rev_const) for p in value
        ])
    if isinstance(value, PreparedFunction):
        return value.get_type()
    if value == NO_VALUE:
        return VoidType()

    raise DataIntegrityError("Unknown value {} {}".format(type(value), value))


class Object(Bunch):
    # Any fields we want to keep out of the bunch dictionary go here
    type_references = None

    def __init__(self, properties_and_values):
        # { foo: Cell(5, IntegerType), bar: Cell("hello", StringType) ...}
        for property_name, property_value in properties_and_values.items():
            if not isinstance(property_name, basestring):
                raise DataIntegrityError()
            if property_value is MISSING:
                raise DataIntegrityError()

        self.type_references = []
        super(Object, self).__init__(properties_and_values)

    def get_type_references(self):
        for r in self.type_references:
            if callable(r):
                r = r()
            if r:
                yield r

    def check_assignment(self, property_name, new_value):
        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ObjectType):
                other_property_type = other_type_reference.property_types.get(property_name, MISSING)
                if other_property_type is MISSING:
                    continue

                new_value_property_type = create_crystal_type(new_value, True)
                if not other_property_type.is_copyable_from(new_value_property_type):
                    raise IncompatableAssignmentError()

                if isinstance(other_property_type, ObjectType):
                    try:
                        new_value.create_reference(other_property_type, True)
                    except CreateReferenceError:
                        raise IncompatableAssignmentError()

    def __setattr__(self, property_name, new_value):
        if new_value == MISSING:
            raise DataIntegrityError()

        if property_name not in [ "type_references" ]:
            self.check_assignment(property_name, new_value)

        Bunch.__setattr__(self, property_name, new_value)

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, ObjectType):
            return False

        current_value_type = create_crystal_type(self, True, new_type_reference)
        if not are_bindable(new_type_reference, current_value_type, False, True):
            return False

        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ObjectType):
                if not are_common_properties_compatible(new_type_reference, other_type_reference):
                    return False
        return True

    def create_reference_on_all_child_references(self, new_type_reference):
        for new_property_name, new_property_type in new_type_reference.property_types.items():
            # Identify whether the reference is to an object that also needs constraining with create_reference
            our_property_value = self.get(new_property_name, MISSING)
            if isinstance(our_property_value, Object):
                our_property_value.create_reference(new_property_type, True)

    def store_reference(self, new_type_reference, use_weak_ref):
        if use_weak_ref:
            new_type_reference = weakref.ref(new_type_reference)
        self.type_references.append(new_type_reference)
#
    def create_reference(self, new_type_reference, use_weak_ref):
        if self.is_new_type_reference_legal(new_type_reference):
            if isinstance(new_type_reference, ObjectType):
                self.create_reference_on_all_child_references(new_type_reference)
            self.store_reference(new_type_reference, use_weak_ref)
        else:
            self.is_new_type_reference_legal(new_type_reference)
            raise CreateReferenceError()
