# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from _ast import Expression
from _collections_abc import Iterable

import requests

from rdhlang4.exception_types import FatalException, PreparationException, \
    IncompatableAssignmentError, CreateReferenceError, \
    InvalidApplicationException, DataIntegrityError, \
    CrystalValueCanNotBeGenerated
from rdhlang4.parser.visitor import nop, context_op, literal_op, type_op
from rdhlang4.type_system.core_types import UnitType, ObjectType, Type, VoidType, \
    merge_types, AnyType, FunctionType, IntegerType, BooleanType, StringType, \
    InferredType, OneOfType, ListType, PythonFunction, RemoveRevConst
from rdhlang4.type_system.values import Object, List, \
    get_manager, create_crystal_type
from rdhlang4.utils import InternalMarker, MISSING, NO_VALUE, spread_dict


class BreakException(Exception):

    def __init__(self, mode, value, opcode=None, caused_by=None):
        self.mode = mode
        self.value = value
        self.opcode = opcode
        self.caused_by = caused_by
        if isinstance(value, BreakException):
            raise DataIntegrityError()

    def __str__(self):
        result = "BreakException<{}: {}>".format(self.mode, self.value)
        if self.caused_by:
            result = "{}\n{}".format(result, self.caused_by)
        return result


class TypeErrorFactory(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, opcode=None, caused_by=None):
        error = Object({
            "type": "TypeError",
        })
        if self.message:
            error.message = self.message
        return BreakException("exception", error, opcode=opcode, caused_by=caused_by)

    def get_type(self):
        properties = {
            "type": UnitType("TypeError")
        }
        if self.message:
            properties["message"] = UnitType(self.message)
        return ObjectType(properties, True)


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
        if not isinstance(self.data, Iterable):
            raise PreparationException()
        self.expressions = [
            enrich_opcode(e, visitor) for e in self.data["expressions"]
        ]

    def get_break_types(self, context):
        expressions_break_types = []
        value_type = MISSING

        for expression in self.expressions:
            value_type, expression_break_types = get_expression_break_types(expression, context, MISSING)
            expressions_break_types.append(expression_break_types)
            if value_type is MISSING:
                break

        if value_type is not MISSING:
            expressions_break_types = expressions_break_types + [{ "value": value_type }]

        return merge_break_types(expressions_break_types)

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
        self.function_raw_data_type, self.other_break_types = get_expression_break_types(self.function, context, MISSING)

        if not self.function_raw_data_type is MISSING:
            try:
                self.function_data = self.function_raw_data_type.get_crystal_value()
            except CrystalValueCanNotBeGenerated as e:
                pass

        break_types = [
            self.other_break_types
        ]

        function = None
        try:
            if self.function_data:
                function = PreparedFunction(self.function_data, context)
        except PreparationException:
            pass

        if function: 
            break_types.append({
                "value": function.get_type()
            })
        else:
            break_types.append({
                "exception": self.PREPARATION_ERROR.get_type()
            })
            if self.function_raw_data_type is not MISSING:
                break_types.append({
                    "value": AnyType()
                })

        return merge_break_types(break_types)

    def jump(self, context):
        try:
            function = PreparedFunction(self.function_data, context)
            raise BreakException("value", function)
        except PreparationException as e:
            raise self.PREPARATION_ERROR(caused_by=e)


class JumpOpcode(Opcode):
    MISSING_FUNCTION = TypeErrorFactory("JumpOpcode: missing_function")
    INVALID_ARGUMENT = TypeErrorFactory("JumpOpcode: invalid_argument")
    UNKNOWN_BREAK_MODE = TypeErrorFactory("JumpOpcode: unknown_break_mode")
    PYTHON_EXCEPTION = TypeErrorFactory("JumpOpcode: python_exception")

    def __init__(self, data, visitor):
        self.function = enrich_opcode(data["function"], visitor)
        self.argument = enrich_opcode(data.get("argument", nop()), visitor)

    def get_break_types(self, context):
        function_type, function_evaluation_break_types = get_expression_break_types(self.function, context, MISSING)
        argument_type, argument_break_types = get_expression_break_types(self.argument, context, MISSING)

        break_types = [ argument_break_types, function_evaluation_break_types ]

        if isinstance(function_type, FunctionType) and argument_type is not MISSING:
            break_types.append(function_type.break_types)
            if not function_type.argument_type.is_copyable_from(argument_type, {}):
                break_types.append({
                    "exception": self.INVALID_ARGUMENT.get_type()
                })
        elif isinstance(function_type, PythonFunction):
            break_types.append({
                "exception": self.PYTHON_EXCEPTION.get_type(),
                "return": AnyType()
            })
        else:
            break_types.extend([{
                "exception": self.MISSING_FUNCTION.get_type()
            }, {
                "exception": self.INVALID_ARGUMENT.get_type()
            }, {
                "exception": self.UNKNOWN_BREAK_MODE.get_type()
            }])

            if function_type is not MISSING and argument_type is not MISSING:
                break_types.append({
                    "return": AnyType(),
                    "exit": IntegerType()
                })

        return merge_break_types(break_types)

    def jump(self, context):
        function_type, _ = get_expression_break_types(self.function, context, MISSING)

        argument = evaluate(self.argument, context)
        function = evaluate(self.function, context)

        try:
            jump_to_function(function, argument)
        except BreakException as e:
            if isinstance(function_type, (FunctionType, PythonFunction)):
                raise
            if e.mode == "return":
                raise
            if e.mode == "exit" and isinstance(e.value, int):
                raise
            raise self.UNKNOWN_BREAK_MODE(self)


def jump_to_function(function, argument):
    if isinstance(function, PreparedFunction):
        try:
            if argument is NO_VALUE:
                function.jump()
            else:
                function.jump(argument)
        except InvalidArgumentException:
            raise JumpOpcode.INVALID_ARGUMENT()
    elif callable(function):
        try:
            result = function(*getattr(argument, "args", []), **getattr(argument, "kwargs", {}))
        except Exception as e:
            print("Python Exception: {}".format(e.args))
            raise JumpOpcode.PYTHON_EXCEPTION()
        raise BreakException("value", result)
    else:
        raise JumpOpcode.MISSING_FUNCTION()

    raise FatalException()


class LoopOpcode(Opcode):

    def __init__(self, data, visitor):
        super(LoopOpcode, self).__init__(data)
        self.code = enrich_opcode(self.data["code"], visitor)

    def get_break_types(self, context):
        _, code_break_types = get_expression_break_types(self.code, context, MISSING)
        return code_break_types

    def jump(self, context):
        while True:
            evaluate(self.code, context)


class ConditionalOpcode(Opcode):
    INVALID_CONDITION_VALUE = TypeErrorFactory("ConditionalOpcode: invalid_condition_value")

    def __init__(self, data, visitor):
        super(ConditionalOpcode, self).__init__(data)
        self.condition = enrich_opcode(self.data["condition"], visitor)
        self.true_code = enrich_opcode(self.data["true_code"], visitor)
        self.false_code = enrich_opcode(self.data["false_code"], visitor)

    def get_break_types(self, context):
        condition_type, condition_break_types = get_expression_break_types(self.condition, context, MISSING)

        break_types = [
            condition_break_types,
            self.true_code.get_break_types(context),
            self.false_code.get_break_types(context)
        ]

        if not BooleanType().is_copyable_from(condition_type, {}):
            break_types.append({
                "exception": self.INVALID_CONDITION_VALUE.get_type()
            })

        return merge_break_types(break_types)

    def jump(self, context):
        condition = evaluate(self.condition, context)
        if not isinstance(condition, bool):
            raise self.INVALID_CONDITION_VALUE()

        if condition is True:
            result = evaluate(self.true_code, context)
        else:
            result = evaluate(self.false_code, context)
        raise BreakException("value", result)


class TransformBreak(Opcode):

    def __init__(self, data, visitor):
        super(TransformBreak, self).__init__(data)
        if "code" in self.data:
            self.expression = enrich_opcode(self.data["code"], visitor)
            if "input" not in self.data:
                raise PreparationException("input missing in transform opcode")
            self.input = self.data["input"]
        else:
            self.expression = None
            self.input = None
        if "output" not in self.data:
            raise PreparationException("output missing in transform opcode")

        self.output = self.data["output"]

    def get_break_types(self, context):
        if self.expression:
            break_types = self.expression.get_break_types(context)
            if self.input in break_types:
                break_types = merge_break_types([
                    break_types, { self.output: break_types.pop(self.input) }
                ])
        else:
            break_types = {
                self.output: VoidType()
            }
        return break_types

    def jump(self, context):
        if self.expression:
            try:
                self.expression.jump(context)
            except BreakException as e:
                if e.mode == self.input:
                    raise BreakException(self.output, e.value)
                else:
                    raise
        else:
            raise BreakException(self.output, NO_VALUE)
        raise FatalException()


class AssignmentOpcode(Opcode):
    INVALID_ASSIGNMENT = TypeErrorFactory("AssignmentOpcode: invalid_assignment")

    def __init__(self, data, visitor):
        self.dereference = enrich_opcode(data["dereference"], visitor)
        self.rvalue = enrich_opcode(data["rvalue"], visitor)

    def get_break_types(self, context):
        if not isinstance(get_expression_break_types(self.dereference, context, MISSING)[0], Type):
            import pydevd
            pydevd.settrace()
        dereference_type, dereference_break_types = get_expression_break_types(self.dereference, context, MISSING)
        rvalue_type, rvalue_break_types = get_expression_break_types(self.rvalue, context, MISSING)
        break_types = [
            dereference_break_types, rvalue_break_types
        ]
        if dereference_type is not MISSING and rvalue_type is not MISSING:
            break_types.append({ "value": VoidType() })
        if not isinstance(dereference_type, Type) or not dereference_type.is_copyable_from(rvalue_type, {}):
            break_types.append({
                "exception": self.INVALID_ASSIGNMENT.get_type(),
            })
        return merge_break_types(break_types)

    def jump(self, context):
        reference, of = self.dereference.get_reference_and_of(context, check_reference_exists=False)
        new_value = evaluate(self.rvalue, context)
        try:
            if isinstance(reference, str):
                setattr(of, reference, new_value)
            if isinstance(reference, int):
                of[reference] = new_value
        except IncompatableAssignmentError:
            raise self.INVALID_ASSIGNMENT(self)

        raise BreakException("value", NO_VALUE)


def clone_literal_value(value):
    if isinstance(value, (int, bool, str)):
        return value
    if isinstance(value, list):
        return List(value)
    if isinstance(value, dict):
        return Object({
            k: clone_literal_value(v) for k, v in value.items()
        })
    raise DataIntegrityError()


class LiteralValueOpcode(Opcode):

    def __init__(self, data, visitor):
        super(LiteralValueOpcode, self).__init__(data)
        if "value" not in self.data:
            raise PreparationException("value missing in literal opcode")

        self.value = self.data["value"]
        self.type = create_crystal_type(self.value, True)

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
        if "properties" not in self.data:
            raise PreparationException("properties missing in new_object opcode")
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
                "value": ObjectType(value_type, True)
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


class NewTupleOpcode(Opcode):

    def __init__(self, data, visitor):
        super(NewTupleOpcode, self).__init__(data)
        self.values = [ enrich_opcode(v, visitor) for v in self.data["values"] ]

    def get_break_types(self, context):
        value_types = []
        other_breaks_types = []

        for sub_value in self.values:
            sub_value_type, sub_value_break_types = get_expression_break_types(sub_value, context)
            other_breaks_types.append(sub_value_break_types)
            value_types.append(sub_value_type)

        return merge_break_types(
            other_breaks_types + [{
                "value": ListType(value_types, VoidType(), True)
            }]
        )

    def jump(self, context):
        raise BreakException(
            "value",
            List([ evaluate(value, context) for value in self.values ])
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
            }, True)
            break_types.append({
                "value": combined_value_type
            })
        else:
            break_types.append({
                "value": ObjectType({}, True),
                "exception": self.MISSING_OBJECTS.get_type()
            })

        return merge_break_types(break_types)

    def jump(self, context):
        first = evaluate(self.first, context)
        second = evaluate(self.second, context)

        if not isinstance(first, Object) or not isinstance(second, Object):
            raise self.MISSING_OBJECTS()

        result = dict(first)
        result.update(second)

        raise BreakException("value", Object(result))


def BinaryOpcode(func, result_type, name):

    class NewOpcode(Opcode):
        MISSING_INTEGERS = TypeErrorFactory("{}: missing_integers".format(name))

        def __init__(self, data, visitor):
            super(NewOpcode, self).__init__(data)
            self.lvalue = enrich_opcode(self.data["lvalue"], visitor)
            self.rvalue = enrich_opcode(self.data["rvalue"], visitor)

        def get_break_types(self, context):
            lvalue_type, lexpression_break_types = get_expression_break_types(self.lvalue, context, MISSING)
            rvalue_type, rexpression_break_types = get_expression_break_types(self.rvalue, context, MISSING)

            int_type = IntegerType()
            self_break_types = []

            if lvalue_type is MISSING or rvalue_type is MISSING or not int_type.is_copyable_from(lvalue_type, {}) or not int_type.is_copyable_from(rvalue_type, {}):
                self_break_types.append({
                    "exception": self.MISSING_INTEGERS.get_type()
                })

            return merge_break_types(self_break_types + [
                lexpression_break_types,
                rexpression_break_types, {
                    "value": result_type
                }
            ])

        def jump(self, context):
            lvalue = evaluate(self.lvalue, context)
            rvalue = evaluate(self.rvalue, context)
            if not isinstance(lvalue, int) or not isinstance(rvalue, int):
                raise self.MISSING_INTEGERS()
            result = func(lvalue, rvalue)
            raise BreakException(
                "value",
                result
            )

    return NewOpcode


class NegationOpcode(Opcode):
    MISSING_INTEGERS = TypeErrorFactory("negation: missing_integers")

    def __init__(self, data, visitor):
        super(NegationOpcode, self).__init__(data)
        self.expression = enrich_opcode(self.data["expression"], visitor)

    def get_break_types(self, context):
        expression_type, expression_break_types = get_expression_break_types(self.expression, context, MISSING)

        int_type = IntegerType()
        self_break_types = []

        if expression_type is MISSING or not int_type.is_copyable_from(expression_type, {}):
            self_break_types.append({
                "exception": self.MISSING_INTEGERS.get_type()
            })

        return merge_break_types(self_break_types + [
            expression_break_types, {
                "value": int_type
            }
        ])

    def jump(self, context):
        value = evaluate(self.expression, context)
        if not isinstance(value, int):
            raise self.MISSING_INTEGERS()
        raise BreakException(
            "value",
            -value
        )


class NotOpcode(Opcode):
    MISSING_BOOLEAN = TypeErrorFactory("NotOpcode: missing_boolean")

    def __init__(self, data, visitor):
        super(NotOpcode, self).__init__(data)
        self.expression = enrich_opcode(self.data["expression"], visitor)

    def get_break_types(self, context):
        expression_type, expression_break_types = get_expression_break_types(self.expression, context, MISSING)
        self_break_types = []
        if not BooleanType().is_copyable_from(expression_type, {}):
            self_break_types.append({
                "exception": self.MISSING_BOOLEAN.get_type(),
            })
        if expression_type is not MISSING:
            self_break_types.append({
                "value": BooleanType()
            })
        return merge_break_types(
            self_break_types + [ expression_break_types ]
        )

    def jump(self, context):
        value = evaluate(self.expression, context)
        if not isinstance(value, bool):
            raise self.MISSING_BOOLEAN()
        raise BreakException("value", not value)


class DereferenceOpcode(Opcode):
    INVALID_DEREFERENCE = TypeErrorFactory("DereferenceOpcode: invalid_dereference")

    def __init__(self, data, visitor):
        super(DereferenceOpcode, self).__init__(data)
        self.reference = enrich_opcode(self.data["reference"], visitor)
        self.of = enrich_opcode(self.data["of"], visitor)

    def get_break_types(self, context):
        reference_type, reference_break_types = get_expression_break_types(self.reference, context)

        invalid_dereference_possible = False

        of_type, of_break_types = get_expression_break_types(self.of, context)
        break_types = [ reference_break_types, of_break_types ]

        crystal_reference_value = reference_type.get_crystal_value()

        if isinstance(of_type, ObjectType) and isinstance(crystal_reference_value, str):
            if crystal_reference_value in of_type.property_types:
                value_type = of_type.property_types[crystal_reference_value]
            else:
                invalid_dereference_possible = True
                value_type = AnyType()  # TODO wildcard types
        elif isinstance(of_type, ListType) and isinstance(crystal_reference_value, int):
            if len(of_type.entry_types) > crystal_reference_value:
                value_type = of_type.entry_types[crystal_reference_value]
            else:
                invalid_dereference_possible = True
                if not isinstance(of_type.wildcard_type, VoidType):
                    value_type = of_type.wildcard_type
                else:
                    value_type = MISSING
        else:
            invalid_dereference_possible = True
            value_type = AnyType()

        if invalid_dereference_possible:
            break_types.append({
                "exception": self.INVALID_DEREFERENCE.get_type()
            })

        if value_type is not MISSING:
            break_types.append({
                "value": value_type
            })

        return merge_break_types(break_types)

    def get_reference_and_of(self, context, check_reference_exists=True):
        of = evaluate(self.of, context)

        reference = evaluate(self.reference, context)

        if hasattr(of, "__dict__") and not isinstance(of, List):
            if not isinstance(reference, str):
                raise self.INVALID_DEREFERENCE()
            if check_reference_exists and not hasattr(of, reference):
                raise self.INVALID_DEREFERENCE()
        elif isinstance(of, Iterable):
            if not isinstance(reference, int):
                raise self.INVALID_DEREFERENCE()
            if len(of) <= reference:
                raise self.INVALID_DEREFERENCE()

        return reference, of

    def jump(self, context):
        reference, of = self.get_reference_and_of(context)

        if isinstance(reference, str):
            value = getattr(of, reference)
        if isinstance(reference, int):
            value = of[reference]

        raise BreakException("value", value)

    def __repr__(self):
        return "Dereference< {}.{} >".format(self.of, self.reference)


def dynamic_get_reference_and_of(context, reference):
    argument = getattr(context, "argument", MISSING)
    if argument is not MISSING and isinstance(argument, Object) and reference in argument:
        return reference, argument

    local = getattr(context, "local", MISSING)
    if local is not MISSING and isinstance(local, Object) and reference in local:
        return reference, local

    outer = getattr(context, "outer", MISSING)
    if outer is not MISSING and isinstance(outer, Object):
        return dynamic_get_reference_and_of(outer, reference)

    return MISSING  # Meaning we couldn't find it


class DynamicDereferenceOpcode(Opcode):
    INVALID_DEREFERENCE = TypeErrorFactory("DynamicDereferenceOpcode: invalid_dereference")

    def __init__(self, data, visitor):
        super(DynamicDereferenceOpcode, self).__init__(data)
        self.reference = enrich_opcode(self.data["reference"], visitor)

    def get_break_types(self, context):
        _, reference_break_types = get_expression_break_types(self.reference, context)

        break_types = [reference_break_types, {
            "value": AnyType(),
            "exception": self.INVALID_DEREFERENCE.get_type()
        }]

        return merge_break_types(break_types)

    def get_reference_and_of(self, context, check_reference_exists=False):
        if check_reference_exists:
            raise ValueError()

        reference = evaluate(self.reference, context)

        search_result = dynamic_get_reference_and_of(context, reference)
        if search_result is not MISSING:
            return search_result

        # Fall back on it being a local variable
        return reference, getattr(context, "local", MISSING)

    def jump(self, context):
        reference, of = self.get_reference_and_of(context)

        value = getattr(of, reference, MISSING)

        if value is MISSING:
            raise self.INVALID_DEREFERENCE()

        raise BreakException("value", value)


IMPORTABLE_THINGS = {
    "requests": requests
}


class ImportOpcode(Opcode):

    def __init__(self, data, visitor):
        super(ImportOpcode, self).__init__(data)
        self.name_expression = enrich_opcode(self.data["name"], visitor)

    def get_break_types(self, context):
        return { "value": AnyType() }

    def jump(self, context):
        name = evaluate(self.name_expression, context)
        thing_to_import = IMPORTABLE_THINGS[name]
        raise BreakException("value", thing_to_import)


def get_context_type(context):
    if not hasattr(context, "_context_type"):
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
        value_type["static"] = create_crystal_type(context.static, set_is_rev_const=False, lazy_object_types=True)
        context._context_type = ObjectType(value_type, False)
    return context._context_type


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
    "loop": LoopOpcode,
    "conditional": ConditionalOpcode,
    "transform": TransformBreak,
    "assignment": AssignmentOpcode,
    "literal": LiteralValueOpcode,
    "new_object": NewObjectOpcode,
    "new_tuple": NewTupleOpcode,
    "merge": MergeOpcode,
    "dereference": DereferenceOpcode,
    "dynamic_dereference": DynamicDereferenceOpcode,
    "import": ImportOpcode,
    "context": ContextOpcode,
    "addition": BinaryOpcode(lambda a, b: a + b, IntegerType(), "addition"),
    "subtraction": BinaryOpcode(lambda a, b: a - b, IntegerType(), "subtraction"),
    "negation": NegationOpcode,
    "multiplication": BinaryOpcode(lambda a, b: a * b, IntegerType(), "multiplication"),
    "division": BinaryOpcode(lambda a, b: int(a / b), IntegerType(), "division"),
    "modulus": BinaryOpcode(lambda a, b: a % b, IntegerType(), "modulus"),
    "gte": BinaryOpcode(lambda a, b: a >= b, BooleanType(), "gte"),
    "lte": BinaryOpcode(lambda a, b: a <= b, BooleanType(), "lte"),
    "gt": BinaryOpcode(lambda a, b: a > b, BooleanType(), "gt"),
    "lt": BinaryOpcode(lambda a, b: a < b, BooleanType(), "lt"),
    "equals": BinaryOpcode(lambda a, b: a == b, BooleanType(), "equals"),
    "not": NotOpcode,
}


def enrich_opcode(data, visitor):
    if visitor:
        data = visitor(data)

    opcode = getattr(data, "opcode", MISSING)
    if opcode is MISSING:
        raise PreparationException("No opcode found in {}".format(data))
    if opcode not in OPCODES:
        raise PreparationException("Unknown opcode {} in {}".format(opcode, data))

    return OPCODES[opcode](data, visitor)


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


def get_is_const(data):
    return data.get("is_const", False)


TYPES = {
    "Any": lambda data: AnyType(is_const=get_is_const(data)),
    "Object": lambda data: ObjectType({
        name: enrich_type(type) for name, type in data["properties"].items()
    }, is_rev_const=False, is_const=get_is_const(data)),
    "List": lambda data: ListType(
        [ enrich_type(type) for type in data["entry_types"] ],
        enrich_type(data["wildcard_type"]),
        is_rev_const=False, is_const=get_is_const(data)
    ),
    "OneOf": lambda data: OneOfType(
        [ enrich_type(type) for type in data["types"] ],
        is_const=get_is_const(data)
    ),
    "Integer": lambda data: IntegerType(is_const=get_is_const(data)),
    "Boolean": lambda data: BooleanType(is_const=get_is_const(data)),
    "Void": lambda data: VoidType(),
    "String": lambda data: StringType(is_const=get_is_const(data)),
    "Function": create_function_type_from_data,
    "Inferred": lambda data: InferredType(is_const=get_is_const(data)),
    "Unit": lambda data: UnitType(data["value"])
}


def enrich_type(data):
    if not isinstance(data, dict):
        raise PreparationException("Unknown type data {}".format(data))
    if "type" not in data:
        raise PreparationException("Missing type in data {}".format(data))
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
                return Object({
                    "opcode": "dereference",
                    "reference": literal_op("argument", None),
                    "of": context_opcode
                })
            local_type = getattr(self.context.types, "local", MISSING)
            if isinstance(local_type, ObjectType) and reference in local_type.property_types:
                return Object({
                    "opcode": "dereference",
                    "reference": literal_op("local", None),
                    "of": context_opcode
                })
            static = getattr(self.context, "static", MISSING)
            if isinstance(static, Object) and reference in static:
                return Object({
                    "opcode": "dereference",
                    "reference": literal_op("static", None),
                    "of": context_opcode
                })
            outer_context = getattr(self.context, "outer", MISSING)
            if outer_context is not MISSING:
                return UnboundDereferenceBinder(outer_context).check_context_for_of(reference, Object({
                    "opcode": "dereference",
                    "reference": literal_op("outer", None),
                    "of": context_opcode
                }))

    def __call__(self, expression):
        if not isinstance(expression, dict):
            return expression

        if expression.get("opcode", MISSING) == "unbound_dereference":
            reference = expression["reference"]
            of_reference = self.check_context_for_of(reference)

            if of_reference:
                code = Object({
                    "opcode": "dereference",
                    "of": of_reference,
                    "reference": literal_op(reference, None)
                })
            else:
                code = Object({
                    "opcode": "dynamic_dereference",
                    "reference": literal_op(reference, None)
                })

            return code

        return expression


class InvalidArgumentException(Exception):
    pass


class PreparedFunction(object):
    INVALID_LOCAL = TypeErrorFactory("PreparedFunction: invalid_local")
    DID_NOT_TERMINATE = TypeErrorFactory("PreparedFunction: did_not_terminate")

    def __init__(self, data, outer_context=NO_VALUE):
        if not isinstance(data, dict):
            raise PreparationException("data for function is not a dict")

        self.data = data

        self.outer_context = outer_context
        self.outer_context_type = get_context_type(outer_context)

        self.static_evaluation_context = Object({
            "outer": self.outer_context,
            "types": Object({
                "outer": self.outer_context_type
            })
        })

        static_unbound_dereference_binder = UnboundDereferenceBinder(self.static_evaluation_context)

        static_code = enrich_opcode(self.data["static"], static_unbound_dereference_binder)
        try:
            self.static = evaluate(static_code, self.static_evaluation_context)
        except BreakException as e:
            raise PreparationException("BreakException while evaluating statics: {}: {}".format(e.mode, e.value))

        if hasattr(self.static, "argument"):
            self.argument_type = enrich_type(self.static.argument)
        else:
            self.argument_type = VoidType()

        self.with_argument_type_context = Object({
            "static": self.static,
            "outer": self.outer_context,
            "types": Object({
                "argument": self.argument_type,
                "outer": self.outer_context_type
            })
        })

        # Don't use an assignment operator, since the context for running local_initializer
        # and for checking that the assigned value of local are different.

        local_initializer = self.data.get("local_initializer", nop())
        local_initializer_unbound_dereference_binder = UnboundDereferenceBinder(self.with_argument_type_context)
        self.local_initializer = enrich_opcode(local_initializer, local_initializer_unbound_dereference_binder)

        local_initializer_type, initializer_break_types = get_expression_break_types(self.local_initializer, self.with_argument_type_context, MISSING)

        if hasattr(self.static, "local"):
            self.local_type = enrich_type(self.static.local).replace_inferred_types(local_initializer_type).visit(RemoveRevConst())
        else:
            self.local_type = VoidType()

        local_initializer_assignment_break_types = {}
        if not self.local_type.is_copyable_from(local_initializer_type, {}):
            local_initializer_assignment_break_types["exception"] = self.INVALID_LOCAL.get_type()

        self.with_argument_and_local_type_context = Object({
            "static": self.static,
            "outer": self.outer_context,
            "types": Object({
                "local": self.local_type,
                "argument": self.argument_type,
                "outer": self.outer_context_type
            })
        })

        if "code" in self.data:
            self.code = enrich_opcode(self.data["code"], UnboundDereferenceBinder(self.with_argument_and_local_type_context))
            code_type, code_break_types = get_expression_break_types(self.code, self.with_argument_and_local_type_context, MISSING)
        else:
            self.code = None
            code_break_types = {}
            code_type = MISSING

        function_might_not_terminate = False
        if local_initializer_type is MISSING and initializer_break_types == {}:
            function_might_not_terminate = True
        if local_initializer_type is not MISSING:
            if code_break_types == {}:
                function_might_not_terminate = True
            if code_type is not MISSING:
                function_might_not_terminate = True
                get_expression_break_types(self.code, self.with_argument_and_local_type_context, MISSING)

        did_not_terminate_break_types = {}
        if function_might_not_terminate:
            did_not_terminate_break_types["exception"] = self.DID_NOT_TERMINATE.get_type()

        if hasattr(self.static, "breaks"):
            break_types_data = self.static.breaks
        else:
            break_types_data = {
                "return": { "type": "Void" }
            }

        default_break_type = MISSING

        if "all" in break_types_data:
            default_break_type = enrich_type(break_types_data["all"])

        self.break_types = {
            mode: enrich_type(type_data) for mode, type_data in break_types_data.items()
        }

        actual_break_types = merge_break_types([
            code_break_types,
            initializer_break_types,
            local_initializer_assignment_break_types,
            did_not_terminate_break_types,
        ])

        for break_mode, actual_break_type in actual_break_types.items():        
            declared_break_type = self.break_types.get(break_mode, default_break_type)

            if isinstance(declared_break_type, InferredType):
                self.break_types[break_mode] = declared_break_type.replace_inferred_types(actual_break_type).visit(RemoveRevConst())
                continue
            if declared_break_type is MISSING:
                raise PreparationException("Code can {} break with {}, but nothing declared".format(break_mode, actual_break_type))
            if not declared_break_type.is_copyable_from(actual_break_type, {}):
                raise PreparationException("Code can {} break with {}, but declared {}".format(break_mode, actual_break_type, declared_break_type))

        self.break_types = {
            break_mode: declared_break_type
            for break_mode, declared_break_type in self.break_types.items()
            if not isinstance(declared_break_type, InferredType)
        }

    def get_type(self):
        return FunctionType(self.argument_type, self.break_types)

    def jump(self, argument=NO_VALUE):
        try:
            evaluation_context = Object({})
            evaluation_context.update(self.static_evaluation_context)
            evaluation_context.update(self.with_argument_and_local_type_context)
            evaluation_context.argument = argument

            try:
                get_manager(evaluation_context).create_reference(
                    ObjectType({ "argument": self.argument_type }, False), False
                )
            except CreateReferenceError:
                raise InvalidArgumentException()

#             try:
#                 get_manager(evaluation_context).create_reference(
#                     ObjectType({ "outer": self.outer_context_type }, False), False
#                 )
#             except CreateReferenceError as e:
#                 raise FatalException("Failed to create reference on outercontext")

            evaluation_context.local = evaluate(self.local_initializer, evaluation_context)

            try:
                get_manager(evaluation_context).create_reference(
                    ObjectType({ "local": self.local_type }, False), False
                )
            except CreateReferenceError:
                raise self.INVALID_LOCAL()

            evaluate(self.code, evaluation_context)

            raise self.DID_NOT_TERMINATE()
        except BreakException as e:
            declared_break_type = self.break_types.get(e.mode, MISSING)
            if declared_break_type is MISSING:
                raise FatalException("Function broke with {} ({}) but this was not declared".format(e.mode, e.value))
            if not declared_break_type.is_copyable_from(create_crystal_type(e.value, True), {}):
                raise FatalException("Function broke with {} ({}) but this could not be copied to {}".format(e.mode, e.value, declared_break_type))
            raise

        raise FatalException("Function did not terminate")

    def invoke(self, argument=NO_VALUE):
        try:
            jump_to_function(self, argument)
        except BreakException as e:
            if e.mode == "return" or e.mode == "exit":
                return e.value
            else:
                raise


def enforce_application_break_mode_constraints(function):
    exit_break_type = function.break_types.get("exit", None)
    if exit_break_type and not IntegerType().is_copyable_from(exit_break_type, {}):
        raise InvalidApplicationException("Application exits with {}, when Integer is expected".format(exit_break_type))
    exception_break_type = function.break_types.get("exception", None)
    if exception_break_type and exception_break_type.is_copyable_from(PrepareOpcode.PREPARATION_ERROR.get_type(), {}):
        raise InvalidApplicationException("Application might exit with preparation error")

def execute(ast):
    executor = PreparedFunction(ast)
    executor.execute()
