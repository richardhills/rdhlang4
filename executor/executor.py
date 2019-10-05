# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from distutils.log import FATAL

from pip._internal.utils.outdated import SELFCHECK_DATE_FMT

from parser.visitor import type, nop, literal_op
from type_system.core_types import ObjectType, IntegerType, BooleanType, \
    OneOfType, VoidType, Type, Object, StringType, UnitType, FunctionType,\
    MISSING
from utils import InternalMarker


MISSING = InternalMarker("MISSING")
NO_VALUE = InternalMarker("NO_VALUE")


class FatalException(Exception):
    pass


class PreparationException(Exception):
    pass


class BreakException(Exception):

    def __init__(self, mode, value):
        self.mode = mode
        self.value = value


def TypeError():
    return BreakException("exception", None)


def TypeErrorType():
    return ObjectType({
        "type": UnitType("TypeError")
    })


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
            new_break_type = OneOfType([previous_break_type, type]).flatten()
            result[mode] = new_break_type
    return result


def get_expression_break_types(expression, context, default_if_missing=MISSING):
    other_break_types = expression.get_break_types(context)
    value_break_types = other_break_types.pop("value", default_if_missing)
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
    def __init__(self, data, visitor):
        self.function = enrich_opcode(data["function"], visitor)

    def get_break_types(self, context):
        function_raw_data_type, other_break_types = get_expression_break_types(self.function, context)
        function_data = function_raw_data_type.get_crystal_value()
        executor = FunctionExecutor(function_data)

        return merge_break_types([ other_break_types ] + {
            "value": executor.get_type()
        })

    def jump(self, context):
        function_raw_data_type, _ = get_expression_break_types(self.function, context)
        function_data = function_raw_data_type.get_crystal_value()
        raise BreakException("value", FunctionExecutor(function_data))

class JumpOpcode(Opcode):
    def __init__(self, data, visitor):
        self.function = enrich_opcode(data["function"], visitor)
        self.argument = enrich_opcode(data.get("argument", nop()), visitor)

    def get_break_types(self, context):
        function_type, function_evaluation_break_types = get_expression_break_types(self.function, context)
        _, argument_break_types = get_expression_break_types(self.argument, context)

        return merge_break_types([
            argument_break_types,
            function_evaluation_break_types,
            function_type.break_types
        ])

    def jump(self, context):
        argument = evaluate(self.argument, context)
        function = evaluate(self.function, context)
        function.invoke(argument)

class BreakOpcode(Opcode):

    def __init__(self, data, visitor):
        super(BreakOpcode, self).__init__(data)
        self.expression = enrich_opcode(self.data["value"], visitor)
        self.type = self.data["type"]

    def get_break_types(self, context):
        self_break_types = []
        value_break_types = {}
        value_type, expression_break_types = get_expression_break_types(self.expression, context)

        if value_type is MISSING:
            self_break_types.append({
                "exception": TypeErrorType()
            })
        else:
            value_break_types = {
                self.type: value_type
            }

        return merge_break_types(self_break_types + [
            expression_break_types,
            value_break_types
        ])

    def jump(self, context):
        raise BreakException(self.type, evaluate(self.expression, context))

class CatchOpcode(Opcode):
    def __init__(self, data, visitor):
        super(CatchOpcode, self).__init__(data)
        self.code = enrich_opcode(self.data["code"], visitor)
        self.type = self.data["type"]

    def get_break_types(self, context):
        code_break_types = self.code.get_break_types(context)
        returned_as_value_type = code_break_types.pop(self.type, MISSING)
        if returned_as_value_type is MISSING:
            returned_as_value_type = {}
        else:
            returned_as_value_type = {
                "value": returned_as_value_type
            }

        return merge_break_types([
            code_break_types, returned_as_value_type
        ])

    def jump(self, context):
        try:
            evaluate(self.code, context)
        except BreakException as e:
            if e.mode == self.type:
                raise BreakException("value", e.value)
            else:
                raise

def guess_literal_value_type(value):
    if isinstance(value, (int, bool, basestring)):
        return UnitType(value)
    if isinstance(value, dict):
        return ObjectType({
            k: guess_literal_value_type(v) for k, v in value.items()
        })
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
                "value": ObjectType(value_type)
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
    def __init__(self, data, visitor):
        super(MergeOpcode, self).__init__(data)
        self.first = enrich_opcode(data["first"], visitor)
        self.second = enrich_opcode(data["second"], visitor)

    def get_break_types(self, context):
        first_value_type, first_other_break_types = get_expression_break_types(self.first, context)
        second_value_type, second_other_break_types = get_expression_break_types(self.second, context)
        combined_value_type = ObjectType({
            property: type for property, type in first_value_type.property_types.items() + second_value_type.property_types.items()
        })

        return merge_break_types(first_other_break_types + second_other_break_types + [{
            "value": combined_value_type
        }])

    def jump(self, context):
        first = evaluate(self.first, context)
        second = evaluate(self.second, context)
        raise BreakException("value", Object({
            property: value for property, value in first.items() + second.items()
        }))

class AdditionOpcode(Opcode):

    def __init__(self, data, visitor):
        super(AdditionOpcode, self).__init__(data)
        self.lvalue = enrich_opcode(self.data["lvalue"], visitor)
        self.rvalue = enrich_opcode(self.data["rvalue"], visitor)

    def get_break_types(self, context):
        lvalue_type, lexpression_break_types = get_expression_break_types(self.lvalue, context)
        rvalue_type, rexpression_break_types = get_expression_break_types(self.rvalue, context)

        int_type = IntegerType()
        self_break_types = []
        if not int_type.is_copyable_from(lvalue_type) or not int_type.is_copyable_from(rvalue_type):
            self_break_types.append({
                "exception": TypeErrorType()
            })

        return merge_break_types(self_break_types + [
            lexpression_break_types,
            rexpression_break_types, {
                "value": IntegerType()
            }
        ])

    def jump(self, context):
        raise BreakException(
            "value",
            evaluate(self.lvalue, context) + evaluate(self.rvalue, context)
        )


class DereferenceOpcode(Opcode):

    def __init__(self, data, visitor):
        super(DereferenceOpcode, self).__init__(data)
        self.reference = enrich_opcode(self.data["reference"], visitor)
        if "of" in data:
            self.of = enrich_opcode(self.data["of"], visitor)
        else:
            self.of = None

    def get_break_types(self, context):
        reference_type, reference_break_types = get_expression_break_types(self.reference, context)
        if self.of:
            of_type, of_break_types = get_expression_break_types(self.of, context)
        else:
            of_type = of_break_types = None

        return {}

    def jump(self, context):
        of = evaluate(self.of, context)

        reference = evaluate(self.reference, context)

        if not isinstance(of, Object):
            raise TypeError()

        value = of[reference]

        raise BreakException("value", value)


class ContextOpcode(Opcode):

    def __init__(self, data, visitor):
        super(ContextOpcode, self).__init__(data)

    def get_break_types(self, context):
        return {}

    def jump(self, context):
        raise BreakException("value", context)


OPCODES = {
    "nop": NopOpcode,
    "comma": CommaOpcode,
    "prepare": PrepareOpcode,
    "jump": JumpOpcode,
    "break": BreakOpcode,
    "catch": CatchOpcode,
    "literal": LiteralValueOpcode,
    "new_object": NewObjectOpcode,
    "merge": MergeOpcode,
    "dereference": DereferenceOpcode,
    "context": ContextOpcode,
    "add": AdditionOpcode
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


TYPES = {
    "Object": lambda data: ObjectType({ name: enrich_type(type) for name, type in data["properties"].items() }),
    "Integer": lambda data: IntegerType(),
    "Boolean": lambda data: BooleanType(),
    "Void": lambda data: VoidType(),
    "String": lambda data: StringType()
}


def enrich_type(data):
    type_constructor = TYPES.get(data["type"], MISSING)
    if type_constructor is MISSING:
        raise PreparationException("Unknown type {}".format(data["type"]))

    return type_constructor(data)


class FunctionExecutor(object):

    def __init__(self, data):
        self.data = data

        self.static_evaluation_context = Object({})
        static_code = enrich_opcode(self.data["static"], None)
        self.static = evaluate(static_code, self.static_evaluation_context)

        self.local_type = enrich_type(self.static.local)
        self.argument_type = enrich_type(self.static.argument)

        def bind_dereferences(expression):
            if isinstance(expression, basestring):
                pass
            if expression["opcode"] == "unbound_dereference":
                reference = expression["reference"]
                of_reference = None

                if reference in ("local", "argument"):
                    of_reference = { "opcode": "context" }
                if isinstance(self.argument_type, ObjectType) and reference in self.argument_type.property_types:
                    of_reference = {
                        "opcode": "dereference",
                        "reference": literal_op("argument"),
                        "of": { "opcode": "context" }
                    }
                if isinstance(self.local_type, ObjectType) and reference in self.local_type.property_types:
                    of_reference = {
                        "opcode": "dereference",
                        "reference": literal_op("local"),
                        "of": { "opcode": "context" }
                    }

                code = {
                    "opcode": "dereference",
                    "reference": literal_op(reference)
                }

                if of_reference:
                    code["of"] = of_reference

                return code
            return expression

        local_initializer = self.data.get("local_initializer", None)
        if local_initializer:
            self.local_initializer = enrich_opcode(local_initializer, bind_dereferences)
        else:
            self.local_initializer = enrich_opcode(nop(), bind_dereferences)

        local_initializer_type, _ = get_expression_break_types(self.local_initializer, self.static_evaluation_context)
        if not self.local_type.is_copyable_from(local_initializer_type):
            raise PreparationException("local_initializer has type {} but locals defined with type {}".format(local_initializer_type, self.local_type))

        self.code = enrich_opcode(self.data["code"], bind_dereferences)

        break_types_data = self.static.get("breaks", {
            "return": { "type": "Void" }
        });

        self.break_types = {
            mode: enrich_type(type_data) for mode, type_data in break_types_data.items()
        }

        self.get_break_types_context = {
            "break_types": self.break_types
        }

        actual_break_types = merge_break_types([
            self.code.get_break_types(self.get_break_types_context),
            self.local_initializer.get_break_types(self.get_break_types_context)
        ])

        for declared_mode, declared_break_type in self.break_types.items():
            actual_break_type = actual_break_types.get(declared_mode, MISSING)
            if actual_break_type is MISSING:
                continue
            if not declared_break_type.is_copyable_from(actual_break_type):
                raise PreparationException("Code {} breaks with {}, but declared {}".format(declared_mode, actual_break_type, declared_break_type))

    def get_type(self):
        return FunctionType(self.argument_type, self.break_types)

    def invoke(self, argument=MISSING):
        try:
            evaluation_context = Object({})
            evaluation_context.update(self.static_evaluation_context)
            evaluation_context.update(self.get_break_types_context)
            if argument is not MISSING:
                evaluation_context["argument"] = argument
            evaluation_context["local"] = evaluate(self.local_initializer, evaluation_context)
            evaluate(self.code, evaluation_context)
        except BreakException as e:
            if e.mode == "return":
                return e.value
            else:
                raise


def execute(ast):
    executor = FunctionExecutor(ast)
    executor.execute()
