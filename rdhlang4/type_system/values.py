# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from _collections_abc import MutableSequence, Iterable
import sys
import threading
import weakref

from munch import Munch

from rdhlang4.exception_types import DataIntegrityError, InvalidCompositeObject, \
    CreateReferenceError, FatalException, IncompatableAssignmentError, \
    InvalidDereferenceError, NoValueError, InvalidSpliceParametersError, \
    InvalidSpliceModificationError
from rdhlang4.type_system.core_types import Type, VISIT_CHILDREN, ObjectType, \
    ListType, UnknownType, UnitType, PythonFunction, NoValueType, CREATE_NEW_TYPE, \
    AnyType, are_bindable, compare_composite_types, CompositeType, OneOfType
from rdhlang4.utils import MISSING, NO_VALUE


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
            if value is NO_VALUE:
                return NoValueType()
            if value is None:
                return UnitType(None)
            if isinstance(value, (list, List)):
                result = ListType([
                    self.find_or_create_crystal_type(p, None) for p in value
                ], OneOfType([ AnyType(is_const=True), NoValueType() ], is_const=True), self.set_is_rev_const)
                result.original_value_id = id(value)
                return result
            if isinstance(value, tuple):
                result = ListType([
                    self.find_or_create_crystal_type(p, None) for p in value
                ], NoValueType(), self.set_is_rev_const)
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
        if isinstance(obj, List):
            manager = ListManager(obj)
        elif hasattr(obj, "__dict__"):
            manager = ObjectManager(obj)
        else:
            raise InvalidCompositeObject()

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

class CompositeManager(object):
    type = None

    def __init__(self, obj):
        self.type_references = []
        self.obj = obj

    def get_type_references(self):
        for r in self.type_references:
            if callable(r):
                r = r()
            if r:
                yield r

    def store_reference(self, new_type_reference, use_weak_ref):
        if use_weak_ref:
            new_type_reference = weakref.ref(new_type_reference)
        self.type_references.append(new_type_reference)

    def create_reference(self, new_type_reference, use_weak_ref):
        if self.is_new_type_reference_legal(new_type_reference):
            if isinstance(new_type_reference, (ObjectType, ListType)):
                self.create_reference_on_all_child_references(new_type_reference)
            self.store_reference(new_type_reference, use_weak_ref)
        else:
            raise CreateReferenceError()

    def is_new_type_reference_legal(self, new_type_reference):
        if isinstance(new_type_reference, AnyType):
            return True
        if not isinstance(new_type_reference, self.type):
            return False

        if new_type_reference.is_rev_const:
            raise FatalException()

        current_value_type = create_crystal_type(self.obj, True, mask_type=new_type_reference)
        if not are_bindable(new_type_reference, current_value_type, False, True, {}):
            return False

        for other_type_reference in self.get_type_references():
            if not compare_composite_types(
                new_type_reference,
                other_type_reference,
                False,
                False,
                {}
            ):
                return False

        return True

    def check_assignment(self, key, new_value):
        new_value_crystal_type = create_crystal_type(new_value, True)
        for other_type_reference in self.get_type_references():
            if isinstance(other_type_reference, CompositeType):
                other_key_type = other_type_reference.get_key_type(key)

                if not other_key_type.is_copyable_from(new_value_crystal_type, {}):
                    raise IncompatableAssignmentError()

                if isinstance(other_key_type, CompositeType):
                    try:
                        get_manager(new_value).create_reference(other_key_type, True)
                    except CreateReferenceError:
                        raise IncompatableAssignmentError()

    def create_reference_on_all_child_references(self, new_type_reference):
        for new_key_name, new_key_type in new_type_reference.get_keys_and_types():
            # Identify whether the reference is to an object that also needs constraining with create_reference
            our_property_value = self.get_key_value(new_key_name, new_key_type)
            if isinstance(new_key_type, (ListType, ObjectType)):
                get_manager(our_property_value).create_reference(new_key_type, True)

    def get_key_value(self, key, accessing_type):
        raise NotImplementedError(self)

class ObjectManager(CompositeManager):
    type = ObjectType

    def __init__(self, obj):
        obj.__class__ = self.create_new_managed_type(obj.__class__)
        super(ObjectManager, self).__init__(obj)

    def get_key_value(self, key, accessing_type):
        if not isinstance(key, str):
            raise InvalidDereferenceError()
        if not hasattr(self.obj, key):
            raise NoValueError()
        return getattr(self.obj, key)

    def set_key_value(self, key, new_value):
        if not isinstance(key, str):
            raise InvalidDereferenceError()
        setattr(self.obj, key, new_value)

    def create_new_managed_type(self, cls):
        object_manager = self

        def new_setattr(self, property_name, new_value):
            if new_value is MISSING:
                raise DataIntegrityError()

            object_manager.check_assignment(property_name, new_value)

            cls.__setattr__(self, property_name, new_value)

        return type(cls.__name__, (cls,), { "__setattr__": new_setattr })


class List(MutableSequence):
    def __init__(self, values, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.wrapped = list(values)
        get_manager(self)

    def __len__(self):
        return len(self.wrapped)

    def __getitem__(self, i):
        return self.wrapped[i]

    def __delitem__(self, i):
        del self.wrapped[i]

    def __setitem__(self, i, v):
        get_manager(self).check_assignment(i, v)
        self.wrapped[i] = v

    def insert(self, i, v):
        get_manager(self).check_assignment(i, v)
        self.wrapped.insert(i, v)

    def __eq__(self, other):
        if isinstance(other, List):
            return self.wrapped == other.wrapped
        else:
            return self.wrapped == other

    def __repr__(self):
        return repr(self.wrapped)

LIST_METHODS = {
    "push": """
        function(Any) {
            return dynamic function(List<outer.argument>) noexit {
                return function(outer.outer.argument) nothrow noexit {
                    exec({
                        "opcode": "splice",
                        "list": code( outer.argument ),
                        "end": code( 0 ),
                        "delete": code( 0 ),
                        "insert": code( [ argument ] )
                    });
                    return;
                };
            };
        }
    """,
    "pop": """
        function(Any) {
            return dynamic function(List<outer.argument>) noexit {
                return function() noexit {
                    outer.outer.argument value = outer.argument[-1];
                    exec({
                        "opcode": "splice",
                        "list": code( outer.argument ),
                        "end": code( 1 ),
                        "delete": code( 1 )
                    });
                    return value;
                };
            };
        }
    """,
    "add": """
        function(Any) {
            return dynamic function(List<outer.argument>) noexit {
                return function(Tuple<Integer, outer.outer.argument>) noexit {
                    exec({
                        "opcode": "splice",
                        "list": code( outer.argument ),
                        "start": code( argument[0] ),
                        "delete": code( 0 ),
                        "insert": code( [ argument[1] ] )
                    });
                    return;
                };
            };
        }
    """,
    "remove": """
        function(Any) {
            return dynamic function(List<outer.argument>) noexit {
                return function(Integer) noexit {
                    exec({
                        "opcode": "splice",
                        "list": code( outer.argument ),
                        "start": code( argument ),
                        "delete": code( 1 )
                    });
                    return;
                };
            };
        }
    """,
}

class ListManager(CompositeManager):
    type = ListType

    def get_key_value(self, key, accessing_type):
        if key in LIST_METHODS:
            from rdhlang4.parser.rdhparser import prepare_code
            factory = prepare_code(
                LIST_METHODS[key], check_application_break_mode_constraints=False, include_stdlib=False
            )
            return factory.invoke(accessing_type.wildcard_type.to_dict()).invoke(self.obj)
        if not isinstance(key, int):
            raise InvalidDereferenceError()
        if key < 0:
            key += len(self.obj)
        if key >= 0 and key < len(self.obj):
            return self.obj[key]
        else:
            raise NoValueError()

    def set_key_value(self, key, new_value):
        if not isinstance(key, int):
            raise InvalidDereferenceError()
        if key < 0:
            key += len(self.obj)
        self.obj[key] = new_value

    def splice(self, start, end, delete, insert):
        if not (bool(isinstance(start, int)) ^ bool(isinstance(end, int))):
            raise InvalidSpliceParametersError()

        if not isinstance(delete, int):
            raise InvalidSpliceParametersError()

        if delete < 0:
            raise InvalidSpliceModificationError()

        if(insert is not MISSING
           and not isinstance(insert, List)
        ):
            raise InvalidSpliceParametersError()    

        if start is MISSING:
            start = len(self.obj) - end

        if start + delete > len(self.obj):
            raise InvalidSpliceParametersError()

        new_list = self.obj.wrapped[:start]
        if insert is not MISSING:
            new_list = new_list + insert.wrapped
        new_list = new_list + self.obj.wrapped[start + delete:]

        for index, value in enumerate(new_list):
            self.check_assignment(index, value)

        for index, value in enumerate(new_list):
            if len(self.obj) > index:
                self.obj[index] = value
            else:
                self.obj.append(value)

        for index in range(len(self.obj) - len(new_list)):
            self.obj.pop()
