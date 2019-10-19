# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from exception_types import FatalException, PreparationException, \
    IncompatableAssignmentError, CreateReferenceError
import json

from parser.visitor import type, nop, literal_op, context_op, \
    symbolic_dereference_ops
from type_system.core_types import ObjectType, IntegerType, BooleanType, \
    OneOfType, VoidType, Type, Object, StringType, UnitType, FunctionType, \
    AnyType, merge_types, InferredType
from utils import InternalMarker, MISSING, NO_VALUE


class BreakException(Exception):

    def __init__(self, mode, value):
        self.mode = mode
        self.value = value


class TypeErrorFactory(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self):
        error = Object({
            "type": "TypeError",
        })
        if self.message:
            error.message = self.message
        return BreakException("exception", error)

    def get_type(self):
        properties = {
            "type": UnitType("TypeError")
        }
        if self.message:
            properties["message"] = UnitType(self.message)
        return ObjectType(properties)


def merge_break_types(breaks_types):
    result = {}
    if not isinstance(breaks_types, list):
        raise FatalException()
    for break_types in breaks_types:
        if not isinstance(break_types, dict):
            raise FatalException()

        for mode, type in break_types.items():
            if not isinstance(type, Type):
                raise FatalException()

            previous_break_type = result.get(mode, VoidType())
            new_break_type = merge_types([previous_break_type, type])
            result[mode] = new_break_type
    return result


THROW_IF_MISSING = InternalMarker("THROW_IF_MISSING")


def get_expression_break_types(expression, context, default_if_missing=THROW_IF_MISSING):
    other_break_types = expression.get_break_types(context)
    value_break_types = other_break_types.pop("value", default_if_missing)
    if value_break_types is THROW_IF_MISSING:
        raise FatalException()
    return value_break_types, other_break_types


class Opcode(object):

    def __init__(self, data):
        self.data = data

    def get_break_types(self, context):
        raise NotImplementedError()

    def jump(self, context):
        raise NotImplementedError()


class NopOpcode(Opcode):

    def __init__(self, data, visitor):
        super(NopOpcode, self).__init__(data)

    def get_break_types(self, context):
        return {
            "value": VoidType()
        }

    def jump(self, context):
        raise BreakException("value", NO_VALUE)


class CommaOpcode(Opcode):

    def __init__(self, data, visitor):
        super(CommaOpcode, self).__init__(data)
        self.expressions = [
            enrich_opcode(e, visitor) for e in self.data["expressions"]
        ]

    def get_break_types(self, context):
        expressions_break_types = []
        value_type = VoidType()

        for expression in self.expressions:
            value_type, expression_break_types = get_expression_break_types(expression, context, VoidType())
            expressions_break_types.append(expression_break_types)

        return merge_break_types(expressions_break_types + [{ "value": value_type }])

    def jump(self, context):
        result = MISSING
        for expression in self.expressions:
            result = evaluate(expression, context)
        if result is MISSING:
            raise TypeError()
        raise BreakException("value", result)


class PrepareOpcode(Opcode):
    PREPARATION_ERROR = TypeErrorFactory("PrepareOpcode: preparation_error")

    def __init__(self, data, visitor):
        self.function = enrich_opcode(data["function"], visitor)
        self.function_raw_data = None
        self.other_break_types = None
        self.function_data = None

    def get_break_types(self, context):
        self.function_raw_data_type, self.other_break_types = get_expression_break_types(self.function, context)
        self.function_data = self.function_raw_data_type.get_crystal_value()

        break_types = [
            self.other_break_types
        ]

        try:
            function = PreparedFunction(self.function_data, context)
            break_types.append({
                "value": function.get_type()
            })
        except PreparationException:
            break_types.append({
                "value": AnyType(),
                "exception": self.PREPARATION_ERROR.get_type()
            })

        return merge_break_types(break_types)

    def jump(self, context):
        function = PreparedFunction(self.function_data, context)
        raise BreakException("value", function)


class JumpOpcode(Opcode):
    MISSING_FUNCTION = TypeErrorFactory("JumpOpcode: missing function")
    INVALID_ARGUMENT = TypeErrorFactory("JumpOpcode: invalid_argument")

    def __init__(self, data, visitor):
        self.function = enrich_opcode(data["function"], visitor)
        self.argument = enrich_opcode(data.get("argument", nop()), visitor)

    def get_break_types(self, context):
        function_type, function_evaluation_break_types = get_expression_break_types(self.function, context, MISSING)
        argument_type, argument_break_types = get_expression_break_types(self.argument, context, MISSING)

        break_types = [ argument_break_types, function_evaluation_break_types ]

        if isinstance(function_type, FunctionType):
            break_types.append(function_type.break_types)
            if not function_type.argument_type.is_copyable_from(argument_type):
                break_types.append({
                    "exception": self.INVALID_ARGUMENT.get_type()
                })
        else:
            break_types.extend([{
                "exception": self.MISSING_FUNCTION.get_type()
            }, {
                "exception": self.INVALID_ARGUMENT.get_type()
            }])

        return merge_break_types(break_types)

    def jump(self, context):
        argument = evaluate(self.argument, context)
        function = evaluate(self.function, context)

        if not isinstance(function, PreparedFunction):
            raise self.MISSING_FUNCTION()

        if argument is NO_VALUE:
            function.jump()
        else:
            function.jump(argument)

        raise FatalException()


class TransformBreak(Opcode):

    def __init__(self, data, visitor):
        super(TransformBreak, self).__init__(data)
        self.expression = enrich_opcode(self.data["code"], visitor)
        self.input = self.data["input"]
        self.output = self.data["output"]

    def get_break_types(self, context):
        break_types = self.expression.get_break_types(context)
        if self.input in break_types:
            break_types[self.output] = break_types.pop(self.input)
        return break_types

    def jump(self, context):
        try:
            self.expression.jump(context)
            
        except BreakException as e:
            if e.mode == self.input:
                raise BreakException(self.output, e.value)
            else:
                raise
        raise FatalException()


class AssignmentOpcode(Opcode):
    INVALID_ASSIGNMENT = TypeErrorFactory("AssignmentOpcode: invalid_assignment")

    def __init__(self, data, visitor):
        self.dereference = enrich_opcode(data["dereference"], visitor)
        self.rvalue = enrich_opcode(data["rvalue"], visitor)

    def get_break_types(self, context):
        dereference_type, dereference_break_types = get_expression_break_types(self.dereference, context)
        rvalue_type, rvalue_break_types = get_expression_break_types(self.rvalue, context)
        break_types = [
            dereference_break_types, rvalue_break_types
        ]
        if not dereference_type.is_copyable_from(rvalue_type):
            break_types.append({
                "exception": self.INVALID_ASSIGNMENT.get_type()
            })
        return merge_break_types(break_types)

    def jump(self, context):
        reference, of = self.dereference.get_reference_and_of(context)
        new_value = evaluate(self.rvalue, context)
        try:
            of[reference] = new_value
        except IncompatableAssignmentError:
            raise self.INVALID_ASSIGNMENT()


def guess_literal_value_type(value):
    if isinstance(value, (int, bool, basestring)):
        return UnitType(value, is_rev_const=True)
    if isinstance(value, dict):
        return ObjectType({
            k: guess_literal_value_type(v) for k, v in value.items()
        }, is_rev_const=True)
    raise PreparationException("Unknown value {}".format(value))


def clone_literal_value(value):
    if isinstance(value, (int, bool, basestring)):
        return value
    if isinstance(value, dict):
        return Object({
            k: clone_literal_value(v) for k, v in value
        })


class LiteralValueOpcode(Opcode):

    def __init__(self, data, visitor):
        super(LiteralValueOpcode, self).__init__(data)
        self.value = self.data["value"]
        self.type = guess_literal_value_type(self.value)

    def get_break_types(self, context):
        return {
            "value": self.type
        }

    def jump(self, context):
        raise BreakException("value", clone_literal_value(self.value))

    def __repr__(self):
        return "\"{}\"".format(self.value)


class NewObjectOpcode(Opcode):

    def __init__(self, data, visitor):
        super(NewObjectOpcode, self).__init__(data)
        self.properties = {
            k: enrich_opcode(v, visitor) for k, v in self.data["properties"].items()
        }

    def get_break_types(self, context):
        value_type = {}
        other_breaks_types = []

        for property, opcode in self.properties.items():
            property_value_type, other_break_types = get_expression_break_types(opcode, context)
            value_type[property] = property_value_type
            other_breaks_types.append(other_break_types)

        return merge_break_types(
            other_breaks_types + [{
                "value": ObjectType(value_type, is_rev_const=True)
            }]
        )

    def get_property_value(self, property_name, context):
        return evaluate(self.properties[property_name], context)

    def jump(self, context):
        raise BreakException(
            "value",
            Object({
                property: self.get_property_value(property, context) for property in self.properties.keys()
            })
        )


class MergeOpcode(Opcode):
    MISSING_OBJECTS = TypeErrorFactory("MergeOpcode: missing_objects")

    def __init__(self, data, visitor):
        super(MergeOpcode, self).__init__(data)
        self.first = enrich_opcode(data["first"], visitor)
        self.second = enrich_opcode(data["second"], visitor)

    def get_break_types(self, context):
        first_value_type, first_other_break_types = get_expression_break_types(self.first, context)
        second_value_type, second_other_break_types = get_expression_break_types(self.second, context)

        break_types = [ first_other_break_types, second_other_break_types ]

        if isinstance(first_value_type, ObjectType) and isinstance(second_value_type, ObjectType):
            combined_value_type = ObjectType({
                property: type for property, type in first_value_type.property_types.items() + second_value_type.property_types.items()
            })
            break_types.append({
                "value": combined_value_type
            })
        else:
            break_types.append({
                "value": ObjectType({}),
                "exception": self.MISSING_OBJECTS.get_type()
            })

        return merge_break_types(break_types)

    def jump(self, context):
        first = evaluate(self.first, context)
        second = evaluate(self.second, context)

        if not isinstance(first, Object) or not isinstance(second, Object):
            raise self.MISSING_OBJECTS()

        raise BreakException("value", Object({
            property: value for property, value in first.items() + second.items()
        }))


class AdditionOpcode(Opcode):
    MISSING_INTEGERS = TypeErrorFactory("AdditionOpcode: missing_integers")

    def __init__(self, data, visitor):
        super(AdditionOpcode, self).__init__(data)
        self.lvalue = enrich_opcode(self.data["lvalue"], visitor)
        self.rvalue = enrich_opcode(self.data["rvalue"], visitor)

    def get_break_types(self, context):
        lvalue_type, lexpression_break_types = get_expression_break_types(self.lvalue, context, MISSING)
        rvalue_type, rexpression_break_types = get_expression_break_types(self.rvalue, context, MISSING)

        int_type = IntegerType()
        self_break_types = []

        if lvalue_type is MISSING or rvalue_type is MISSING or not int_type.is_copyable_from(lvalue_type) or not int_type.is_copyable_from(rvalue_type):
            self_break_types.append({
                "exception": self.MISSING_INTEGERS.get_type()
            })

        return merge_break_types(self_break_types + [
            lexpression_break_types,
            rexpression_break_types, {
                "value": IntegerType()
            }
        ])

    def jump(self, context):
        lvalue = evaluate(self.lvalue, context)
        rvalue = evaluate(self.rvalue, context)
        if not isinstance(lvalue, int) or not isinstance(rvalue, int):
            raise BreakException("exception", self.MISSING_INTEGERS())
        raise BreakException(
            "value",
            lvalue + rvalue
        )


class MultiplicationOpcode(Opcode):
    MISSING_INTEGERS = TypeErrorFactory("MultiplicationOpcode: missing_integers")

    def __init__(self, data, visitor):
        super(MultiplicationOpcode, self).__init__(data)
        self.lvalue = enrich_opcode(self.data["lvalue"], visitor)
        self.rvalue = enrich_opcode(self.data["rvalue"], visitor)

    def get_break_types(self, context):
        lvalue_type, lexpression_break_types = get_expression_break_types(self.lvalue, context, MISSING)
        rvalue_type, rexpression_break_types = get_expression_break_types(self.rvalue, context, MISSING)

        int_type = IntegerType()
        self_break_types = []

        if lvalue_type is MISSING or rvalue_type is MISSING or not int_type.is_copyable_from(lvalue_type) or not int_type.is_copyable_from(rvalue_type):
            self_break_types.append({
                "exception": self.MISSING_INTEGERS.get_type()
            })

        return merge_break_types(self_break_types + [
            lexpression_break_types,
            rexpression_break_types, {
                "value": IntegerType()
            }
        ])

    def jump(self, context):
        lvalue = evaluate(self.lvalue, context)
        rvalue = evaluate(self.rvalue, context)
        if not isinstance(lvalue, int) or not isinstance(rvalue, int):
            raise BreakException("exception", self.MISSING_INTEGERS())
        raise BreakException(
            "value",
            lvalue * rvalue
        )


class DereferenceOpcode(Opcode):
    INVALID_DEREFERENCE = TypeErrorFactory("DereferenceOpcode: invalid_dereference")

    def __init__(self, data, visitor):
        super(DereferenceOpcode, self).__init__(data)
        self.reference = enrich_opcode(self.data["reference"], visitor)
        self.of = enrich_opcode(self.data["of"], visitor)

    def get_break_types(self, context):
        reference_type, reference_break_types = get_expression_break_types(self.reference, context)
        self_break_types = {}
        value_type = None

        of_type, of_break_types = get_expression_break_types(self.of, context)
        crystal_reference_value = reference_type.get_crystal_value()

        if isinstance(of_type, ObjectType) and isinstance(crystal_reference_value, basestring):
            value_type = of_type.property_types.get(crystal_reference_value)

        if value_type is None:
            value_type = AnyType()
            self_break_types = {
                "exception": self.INVALID_DEREFERENCE.get_type()
            }

        return merge_break_types([
            reference_break_types, of_break_types, self_break_types, {
                "value": value_type
            }
        ])

    def get_reference_and_of(self, context):
        of = evaluate(self.of, context)

        reference = evaluate(self.reference, context)

        if not isinstance(of, Object):
            raise self.INVALID_DEREFERENCE()

        if not hasattr(of, reference):
            raise self.INVALID_DEREFERENCE()

        return reference, of

    def jump(self, context):
        reference, of = self.get_reference_and_of(context)

        value = getattr(of, reference)

        raise BreakException("value", value)

    def __repr__(self):
        return "Dereference< {}.{} >".format(self.of, self.reference)

class DynamicDereferenceOpcode(Opcode):
    INVALID_DEREFERENCE = TypeErrorFactory("DynamicDereferenceOpcode: invalid_dereference")

    def __init__(self, data, visitor):
        super(DynamicDereferenceOpcode, self).__init__(data)
        self.reference = enrich_opcode(self.data["reference"], visitor)

    def get_break_types(self, context):
        reference_type, reference_break_types = get_expression_break_types(self.reference, context)

        break_types = [reference_break_types, {
            "value": AnyType(),
            "exception": self.INVALID_DEREFERENCE.get_type()
        }]

        return merge_break_types(break_types)

    def get_reference_and_of(self, context):
        reference = evaluate(self.reference, context)

        argument = context.argument
        if argument and isinstance(argument, Object) and reference in argument:
            return reference, argument

        local = context.local
        if local and isinstance(local, Object) and reference in local:
            return reference, local

        # Fall back on it being a local variable
        return reference, local

    def jump(self, context):
        reference, of = self.get_reference_and_of(context)

        value = getattr(of, reference, MISSING)

        if value is MISSING:
            raise self.INVALID_DEREFERENCE()

        raise BreakException("value", value)


def get_context_type(context):
    value_type = {}
    if context is NO_VALUE:
        return VoidType()
    if hasattr(context, "types"):
        if hasattr(context.types, "argument"):
            value_type["argument"] = context.types.argument
        if hasattr(context.types, "local"):
            value_type["local"] = context.types.local
        if hasattr(context.types, "outer"):
            value_type["outer"] = context.types.outer
    return ObjectType(value_type)


class ContextOpcode(Opcode):

    def __init__(self, data, visitor):
        super(ContextOpcode, self).__init__(data)

    def get_break_types(self, context):
        return {
            "value": get_context_type(context)
        }

    def jump(self, context):
        raise BreakException("value", context)

    def __repr__(self, *args, **kwargs):
        return "Context"


OPCODES = {
    "nop": NopOpcode,
    "comma": CommaOpcode,
    "prepare": PrepareOpcode,
    "jump": JumpOpcode,
    "transform": TransformBreak,
    "assignment": AssignmentOpcode,
    "literal": LiteralValueOpcode,
    "new_object": NewObjectOpcode,
    "merge": MergeOpcode,
    "dereference": DereferenceOpcode,
    "dynamic_dereference": DynamicDereferenceOpcode,
    "context": ContextOpcode,
    "addition": AdditionOpcode,
    "multiplication": MultiplicationOpcode
}


def enrich_opcode(data, visitor):
    if visitor:
        data = visitor(data)
    opcode_type = OPCODES.get(data["opcode"], MISSING)

    if opcode_type is MISSING:
        raise PreparationException("Unknown opcode {}".format(data))

    return opcode_type(data, visitor)


def evaluate(expression, context):
    try:
        expression.jump(context)
    except BreakException as e:
        if e.mode == "value":
            return e.value
        else:
            raise
    return MISSING


def create_function_type_from_data(data):
    return FunctionType(
        enrich_type(data["argument"]), {
            mode: enrich_type(type) for mode, type in data["breaks"].items()
    })


TYPES = {
    "Any": lambda data: AnyType(),
    "Object": lambda data: ObjectType({ name: enrich_type(type) for name, type in data["properties"].items() }),
    "Integer": lambda data: IntegerType(),
    "Boolean": lambda data: BooleanType(),
    "Void": lambda data: VoidType(),
    "String": lambda data: StringType(),
    "Function": create_function_type_from_data,
    "Inferred": lambda data: InferredType()
}


def enrich_type(data):
    type_constructor = TYPES.get(data["type"], MISSING)
    if type_constructor is MISSING:
        raise PreparationException("Unknown type {}".format(data["type"]))

    return type_constructor(data)


class UnboundDereferenceBinder(object):

    def __init__(self, context):
        self.context = context

    def check_context_for_of(self, reference, context_opcode=None):
        if context_opcode is None:
            context_opcode = context_op()
        if hasattr(self.context, "types"):
            argument_type = getattr(self.context.types, "argument", MISSING)
            if isinstance(argument_type, ObjectType) and reference in argument_type.property_types:
                return {
                    "opcode": "dereference",
                    "reference": literal_op("argument", None),
                    "of": context_opcode
                }
            local_type = getattr(self.context.types, "local", MISSING)
            if isinstance(local_type, ObjectType) and reference in local_type.property_types:
                return {
                    "opcode": "dereference",
                    "reference": literal_op("local", None),
                    "of": context_opcode
                }
            outer_context = getattr(self.context, "outer", MISSING)
            if outer_context is not MISSING:
                return UnboundDereferenceBinder(outer_context).check_context_for_of(reference, {
                    "opcode": "dereference",
                    "reference": literal_op("outer", None),
                    "of": context_opcode
                })

    def __call__(self, expression):
        if isinstance(expression, basestring):
            pass
        if expression["opcode"] == "unbound_dereference":
            reference = expression["reference"]
            of_reference = self.check_context_for_of(reference)

            if of_reference:
                code = {
                    "opcode": "dereference",
                    "of": of_reference,
                    "reference": literal_op(reference, None)
                }
            else:
                code = {
                    "opcode": "dynamic_dereference",
                    "reference": literal_op(reference, None)
                }

            return code
        return expression


class PreparedFunction(object):

    def __init__(self, data, outer_context=NO_VALUE):
        self.data = data

        self.static_evaluation_context = Object({})
        static_code = enrich_opcode(self.data["static"], None)
        self.static = evaluate(static_code, self.static_evaluation_context)
        self.outer_context = outer_context
        self.outer_context_type = get_context_type(outer_context)

        self.local_type = enrich_type(self.static.local)
        self.argument_type = enrich_type(self.static.argument)

        self.with_argument_type_context = Object({
            "static": self.static,
            "outer": self.outer_context,
            "types": Object({
                "argument": self.argument_type,
                "outer": self.outer_context_type
            })
        })

        self.with_argument_and_local_type_context = Object({
            "static": self.static,
            "outer": self.outer_context,
            "types": Object({
                "local": self.local_type,
                "argument": self.argument_type,
                "outer": self.outer_context_type
            })
        })

        # Don't use an assignment operator, since the context for running local_initializer
        # and for checking that the assigned value of local are different.

        local_initializer = self.data.get("local_initializer", nop())
        local_initializer_unbound_dereference_binder = UnboundDereferenceBinder(self.with_argument_type_context)
        self.local_initializer = enrich_opcode(local_initializer, local_initializer_unbound_dereference_binder)

        local_initializer_type, initializer_break_types = get_expression_break_types(self.local_initializer, self.with_argument_type_context)

        local_initializer_assignment_break_types = {}
        if not self.local_type.is_copyable_from(local_initializer_type):
            local_initializer_assignment_break_types["exception"] = AssignmentOpcode.INVALID_ASSIGNMENT.get_type()

        self.code = enrich_opcode(self.data["code"], UnboundDereferenceBinder(self.with_argument_and_local_type_context))
        _, code_break_types = get_expression_break_types(self.code, self.with_argument_and_local_type_context, None)

        break_types_data = self.static.get("breaks", {
            "return": { "type": "Void" }
        });

        self.break_types = {
            mode: enrich_type(type_data) for mode, type_data in break_types_data.items()
        }

        actual_break_types = merge_break_types([ code_break_types, initializer_break_types, local_initializer_assignment_break_types ])

        for break_mode, actual_break_type in actual_break_types.items():
            declared_break_type = self.break_types.get(break_mode, MISSING)
            if isinstance(declared_break_type, InferredType):
                self.break_types[break_mode] = actual_break_type
                continue
            if declared_break_type is MISSING:
                raise PreparationException("Code {} breaks with {}, but nothing declared".format(break_mode, actual_break_type))
            if not declared_break_type.is_copyable_from(actual_break_type):
                raise PreparationException("Code {} breaks with {}, but declared {}".format(break_mode, actual_break_type, declared_break_type))

        # Any remaining inferred break types are not thrown by the code
        for break_mode, declared_break_type in self.break_types.items():
            if isinstance(declared_break_type, InferredType):
                del self.break_types[break_mode]

    def get_type(self):
        return FunctionType(self.argument_type, self.break_types)

    def jump(self, argument=NO_VALUE):
        evaluation_context = Object({})
        evaluation_context.update(self.static_evaluation_context)
        evaluation_context.update(self.with_argument_and_local_type_context)
        evaluation_context.argument = argument
        evaluation_context.local = evaluate(self.local_initializer, evaluation_context)

        context_type = ObjectType({
            "local": self.local_type,
            "argument": self.argument_type,
            "outer": self.outer_context_type
        })

        try:
            evaluation_context.create_reference(context_type)
        except CreateReferenceError:
            raise AssignmentOpcode.INVALID_ASSIGNMENT()

        evaluate(self.code, evaluation_context)

    def invoke(self, argument=NO_VALUE):
        try:
            self.jump(argument)
        except BreakException as e:
            if e.mode == "return":
                return e.value
            else:
                raise


def execute(ast):
    executor = PreparedFunction(ast)
    executor.execute()
