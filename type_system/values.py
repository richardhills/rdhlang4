from bunch import Bunch

from exception_types import DataIntegrityError, IncompatableAssignmentError, \
    CreateReferenceError
from type_system.core_types import UnitType, ObjectType, FunctionType, VoidType, \
    BooleanType, IntegerType, StringType, AnyType, TupleType
from utils import NO_VALUE, MISSING


def infer_value_type(value):
    # Need to think about purpose of inferring a type from a value...
    # There are 2 cases I can think of: inferring type of a value in a BreakException
    # to check it matches a function declaration; inferring a type of a literal op code
    from executor.executor import PreparedFunction

    if isinstance(value, (int, bool, basestring)):
        return UnitType(value)
    if isinstance(value, dict):
        return ObjectType({
            k: infer_value_type(v) for k, v in value.items()
        })
    if isinstance(value, list):
        return TupleType([
            infer_value_type(p) for p in value
        ])
    if isinstance(value, PreparedFunction):
        return value.get_type()

    raise DataIntegrityError("Unknown value {} {}".format(type(value), value))

def infer_primitive_type(value):
    from executor.executor import PreparedFunction

    if isinstance(value, (int, bool, basestring)):
        return UnitType(value)
    if isinstance(value, PreparedFunction):
        return FunctionType(VoidType(), {})
    if isinstance(value, Object):
        return ObjectType({})
    if value is NO_VALUE:
        return VoidType()
    raise DataIntegrityError()

def flatten_to_primitive_type(type):
    if isinstance(type, (BooleanType, IntegerType, StringType, AnyType, VoidType, UnitType)):
        return type
    if isinstance(type, ObjectType):
        return ObjectType({})
    if isinstance(type, FunctionType):
        return FunctionType(VoidType(), {})
    raise DataIntegrityError("Unknown type {}".format(type))



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

    def __setattr__(self, property_name, new_value):
        #if new_value == NO_VALUE:
        #    raise DataIntegrityError()
        if new_value == MISSING:
            raise DataIntegrityError()

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
