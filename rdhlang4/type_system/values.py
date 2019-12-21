# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import threading
import weakref

from munch import Munch

from rdhlang4.exception_types import DataIntegrityError, IncompatableAssignmentError, \
    CreateReferenceError, FatalException
from rdhlang4.type_system.core_types import UnitType, ObjectType, VoidType, AnyType, are_bindable, \
    are_common_properties_compatible, ListType, are_common_entries_compatible, \
    PythonFunction, UnknownType, Type, VISIT_CHILDREN, CREATE_NEW_TYPE
from rdhlang4.utils import NO_VALUE, MISSING, RecursiveHelper, \
    RecursiveEntryPoint


class ManagerCache(object):

    def __init__(self):
        self.managers = {}
        self.objects = {}

    def add(self, obj, manager):
        new_ref = weakref.ref(obj, self.on_ref_gc)
        self.managers[id(obj)] = manager
        self.objects[id(obj)] = new_ref

    def get_manager(self, obj):
        return self.managers.get(id(obj), None)

    def on_ref_gc(self, dead_obj):
        del self.managers[id(dead_obj)]
        del self.objects[id(dead_obj)]


MANAGER_CACHE = ManagerCache()


def visit_key_value_for_crystal_type(key, value, mask_type):
    if not isinstance(key, str):
        return False
    if key == "__builtins__":
        return False
    if key == "packages":
        return False
    if key == "CAPI":
        return False
    if mask_type is not None and key not in mask_type.property_types:
        return False
    return True


def is_unknown_type(value):
    if value is sys:
        return True
    if isinstance(value, (tuple, set)):
        return True
    return False


class RecursiveEntry(Type):

    def __init__(self):
        self.result = MISSING

    def bind(self, result):
        self.result = result


class ReplaceAllRecursiveEntries(object):

    def enter(self, element, key=None, obj=None):
        return (VISIT_CHILDREN,)

    def exit(self, original_type=None, new_type=None, key=None, obj=None):
        if isinstance(original_type, RecursiveEntry):
            if isinstance(obj, ObjectType):
                obj._property_types[key] = original_type.result
            if isinstance(obj, ListType):
                obj.entry_types[key] = original_type.result
        return original_type


def create_crystal_type(value, set_is_rev_const, mask_type=None, lazy_object_types=False):
    creator = CrystalTypeCreator(set_is_rev_const, mask_type, lazy_object_types)
    crystal_type = creator.create_crystal_type(value)
    return crystal_type.visit(ReplaceAllRecursiveEntries())


class CrystalTypeCreator(object):

    def __init__(self, set_is_rev_const, top_mask_type=None, lazy_object_types=False):
        self.set_is_rev_const = set_is_rev_const
        self.top_mask_type = top_mask_type
        self.lazy_object_types = lazy_object_types
        self.already_seen = {}

    def create_crystal_type(self, value):
        return self.find_or_create_crystal_type(value, self.top_mask_type)

    def find_or_create_crystal_type(self, value, mask_type):
        if id(value) in self.already_seen:
            return self.already_seen[id(value)]
        else:
            self.already_seen[id(value)] = RecursiveEntry()

        if not isinstance(mask_type, ObjectType):
            mask_type = None

        crystal_type = self.create_crystal_type_for_value(value, mask_type)

        self.already_seen[id(value)].bind(crystal_type)

        return crystal_type

    def create_crystal_type_for_value(self, value, mask_type):
        try:
            from rdhlang4.executor.executor import PreparedFunction

            if is_unknown_type(value):
                return UnknownType()
            if isinstance(value, (int, float, bool, str)):
                return UnitType(value)
            if callable(value):
                return PythonFunction(value)
            if isinstance(value, PreparedFunction):
                return value.get_type()
            if value == NO_VALUE:
                return VoidType()
            if value == None:
                return UnitType(None)
            if isinstance(value, list):
                result = ListType([
                    self.find_or_create_crystal_type(p, None) for p in value
                ], VoidType(), self.set_is_rev_const)
                result.original_value_id = id(value)
                return result
            if isinstance(value, tuple):
                result = ListType([
                    self.find_or_create_crystal_type(p, None) for p in value
                ], VoidType(), self.set_is_rev_const)
                result.original_value_id = id(value)
                return result
            if isinstance(value, dict):
                if self.lazy_object_types:
                    return LazyCrystalObjectType(value)
                else:
                    return self.create_object_type_from_dict(value, mask_type)
            if hasattr(value, "__dict__"):
                if self.lazy_object_types:
                    return LazyCrystalObjectType(value.__dict__)
                else:
                    return self.create_object_type_from_dict(value.__dict__, mask_type)
        except DataIntegrityError as e:
            raise
    
        return UnknownType()
    #    raise DataIntegrityError("Unknown value {} {}".format(type(value), value))

    def create_object_type_from_dict(self, dict, mask_type):
        return ObjectType(
            self.create_object_property_types_from_dict(dict, mask_type),
            self.set_is_rev_const
        )
    
    def create_object_property_types_from_dict(self, dict, mask_type):
        return {
            k: self.find_or_create_crystal_type(v, mask_type.property_types.get(k, None) if mask_type else None)
            for k, v in dict.items()
            if visit_key_value_for_crystal_type(k, v, mask_type)
        }


create_crystal_type_thread_local = threading.local()

# @RecursiveEntryPoint(create_crystal_type_thread_local)
# def create_crystal_type(value, set_is_rev_const, mask_type=None, lazy_object_types=False):
#     result = nested_create_crystal_type(value, set_is_rev_const, mask_type=mask_type, lazy_object_types=lazy_object_types)
#     return replace_recursive_entries(result)
# 
# 
# @RecursiveHelper(RecursiveEntry, create_crystal_type_thread_local, RecursiveEntry.bind)
# def nested_create_crystal_type(value, set_is_rev_const, mask_type=None, lazy_object_types=False):
#     try:
#         from rdhlang4.executor.executor import PreparedFunction
# 
#         if not isinstance(mask_type, ObjectType):
#             mask_type = None
# 
#         if is_unknown_type(value):
#             return UnknownType()
#         if isinstance(value, (int, float, bool, str)):
#             return UnitType(value)
#         if callable(value):
#             return PythonFunction(value)
#         if isinstance(value, PreparedFunction):
#             return value.get_type()
#         if value == NO_VALUE:
#             return VoidType()
#         if value == None:
#             return UnitType(None)
#         if isinstance(value, list):
#             result = ListType([
#                 nested_create_crystal_type(p, set_is_rev_const) for p in value
#             ], VoidType(), set_is_rev_const)
#             result.original_value_id = id(value)
#             return result
#         if isinstance(value, tuple):
#             result = ListType([
#                 nested_create_crystal_type(p, set_is_rev_const) for p in value
#             ], VoidType(), set_is_rev_const)
#             result.original_value_id = id(value)
#             return result
#         if isinstance(value, dict):
#             if lazy_object_types:
#                 return LazyCrystalObjectType(value)
#             else:
#                 return create_object_type_from_dict(value, set_is_rev_const, mask_type)
#         if hasattr(value, "__dict__"):
#             if lazy_object_types:
#                 return LazyCrystalObjectType(value.__dict__)
#             else:
#                 return create_object_type_from_dict(value.__dict__, set_is_rev_const, mask_type)
#     except DataIntegrityError as e:
#         raise
# 
#     return UnknownType()
# #    raise DataIntegrityError("Unknown value {} {}".format(type(value), value))


class LazyCrystalObjectType(ObjectType):

    def __init__(self, value_dict, *args, **kwargs):
        super(LazyCrystalObjectType, self).__init__({}, True, *args, **kwargs)
        if not isinstance(value_dict, dict):
            raise DataIntegrityError()
        self.value_dict = value_dict
        self.initialized = False

    def is_copyable_from(self, other, result_cache):
        self.check_initialized()
        return super(LazyCrystalObjectType, self).is_copyable_from(other, result_cache)

    def replace_inferred_types(self):
        raise NotImplementedError()

    def get_crystal_value(self):
        raise NotImplementedError()

    @property
    def property_types(self):
        self.check_initialized()
        return self._property_types

    def check_initialized(self):
        if not self.initialized:
            self.resolve()
            self.initialized = True

    def resolve(self):
        creator = CrystalTypeCreator(self.is_rev_const, None, True)

        self._property_types = creator.create_object_property_types_from_dict(
            self.value_dict, None
        )

    def visit(self, visitor, key=None, obj=None):
        if self.initialized:
            return super(LazyCrystalObjectType, self).visit(visitor)
        else:
            enter_result = visitor.enter(self, key=key, obj=obj)
            new_type = self
            if CREATE_NEW_TYPE in enter_result:
                new_type = LazyCrystalObjectType(self.value_dict)
            return visitor.exit(new_type=new_type, original_type=self, key=key, obj=obj)

    def __repr__(self, *args, **kwargs):
        return "LazyCrystalObjectType<{}>".format(self.value_dict)


def get_manager(obj):
    manager = MANAGER_CACHE.get_manager(obj)
    if manager is None:
        if isinstance(obj, list):
            manager = ListManager(obj)
        elif isinstance(obj, dict) or hasattr(obj, "__dict__"):
            manager = ObjectManager(obj)

        if manager:
            MANAGER_CACHE.add(obj, manager)

    return manager


class Object(Munch):

    def __init__(self, properties_and_values):
        # { foo: Cell(5, IntegerType), bar: Cell("hello", StringType) ...}
        for property_name, property_value in properties_and_values.items():
            if not isinstance(property_name, str):
                raise DataIntegrityError()
            if property_value is MISSING:
                raise DataIntegrityError()
        super(Object, self).__init__(properties_and_values)
        get_manager(self)


class ObjectManager(object):

    def __init__(self, obj):
        self.obj = obj
        self.type_references = []
        obj.__class__ = self.create_new_managed_type(obj.__class__)

    def create_new_managed_type(self, cls):
        object_manager = self

        def new_setattr(self, property_name, new_value):
            if new_value == MISSING:
                raise DataIntegrityError()

            object_manager.check_assignment(property_name, new_value)

            cls.__setattr__(self, property_name, new_value)

        return type(cls.__name__, (cls,), { "__setattr__": new_setattr })

    def get_type_references(self):
        for r in self.type_references:
            if callable(r):
                r = r()
            if r:
                yield r

    def check_assignment(self, property_name, new_value):
        new_value_property_type = create_crystal_type(new_value, True)
        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ObjectType):
                other_property_type = other_type_reference.property_types.get(property_name, MISSING)
                if other_property_type is MISSING:
                    continue

                if not other_property_type.is_copyable_from(new_value_property_type, {}):
                    raise IncompatableAssignmentError()

                if isinstance(other_property_type, ObjectType):
                    try:
                        get_manager(new_value).create_reference(other_property_type, True)
                    except CreateReferenceError:
                        raise IncompatableAssignmentError()

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, ObjectType):
            return False

        current_value_type = create_crystal_type(self.obj, True, mask_type=new_type_reference)
        if not are_bindable(new_type_reference, current_value_type, False, True, {}):
            return False

        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ObjectType):
                if not are_common_properties_compatible(new_type_reference, other_type_reference, {}):
                    return False
        return True

    def create_reference_on_all_child_references(self, new_type_reference):
        for new_property_name, new_property_type in new_type_reference.property_types.items():
            # Identify whether the reference is to an object that also needs constraining with create_reference
            our_property_value = getattr(self.obj, new_property_name, MISSING)
            if isinstance(new_property_type, (ListType, ObjectType)):
                get_manager(our_property_value).create_reference(new_property_type, True)

    def store_reference(self, new_type_reference, use_weak_ref):
        if use_weak_ref:
            new_type_reference = weakref.ref(new_type_reference)
        self.type_references.append(new_type_reference)

    def create_reference(self, new_type_reference, use_weak_ref):
        if self.is_new_type_reference_legal(new_type_reference):
            if isinstance(new_type_reference, ObjectType):
                self.create_reference_on_all_child_references(new_type_reference)
            self.store_reference(new_type_reference, use_weak_ref)
        else:
            raise CreateReferenceError()


class List(list):

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        get_manager(self)


class ListManager(object):

    def __init__(self, list):
        self.list = list
        self.type_references = []
        list.__class__ = self.create_new_managed_type(list.__class__)

    def create_new_managed_type(self, cls):
        list_manager = self

        class NewManagedType(cls):

            def __setitem__(self, index, new_value):
                if new_value == MISSING:
                    raise DataIntegrityError()
        
                list_manager.check_assignment(index, new_value)
        
                super(List, self).__setitem__(index, new_value)

        return NewManagedType

    def get_type_references(self):
        for r in self.type_references:
            if callable(r):
                r = r()
            if r:
                yield r

    def check_assignment(self, index, new_value):
        new_value_type = create_crystal_type(new_value, True)

        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ListType):
                if len(other_type_reference.entry_types) >= index:
                    entry_type = other_type_reference.entry_types[index]
                else:
                    entry_type = other_type_reference.wildcard_type

                if not entry_type.is_copyable_from(new_value_type, {}):
                    return False

        return True

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, ListType):
            return False

        current_value_type = create_crystal_type(self, True, new_type_reference)
        if not are_bindable(new_type_reference, current_value_type, False, True, {}):
            return False

        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, ListType):
                if not are_common_entries_compatible(new_type_reference, other_type_reference):
                    return False
        return True

    def create_reference_on_all_child_references(self, new_type_reference):
        for index, new_entry_type in enumerate(new_type_reference.entry_types):
            # Identify whether the reference is to a thing that also needs constraining with create_reference
            our_property_value = self[index]
            if isinstance(our_property_value, (Object, List)):
                get_object_manager(our_property_value).create_reference(new_entry_type, True)

    def store_reference(self, new_type_reference, use_weak_ref):
        if use_weak_ref:
            new_type_reference = weakref.ref(new_type_reference)
        self.type_references.append(new_type_reference)

    def create_reference(self, new_type_reference, use_weak_ref):
        if self.is_new_type_reference_legal(new_type_reference):
            if isinstance(new_type_reference, ListType):
                self.create_reference_on_all_child_references(new_type_reference)
            self.store_reference(new_type_reference, use_weak_ref)
        else:
            raise CreateReferenceError()
