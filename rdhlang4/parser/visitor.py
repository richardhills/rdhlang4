# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from rdhlang4.exception_types import FatalException
from rdhlang4.parser.langVisitor import langVisitor
from rdhlang4.type_system.values import Object, List
from rdhlang4.utils import spread_dict, MISSING, InternalMarker, default


class ParseError(Exception):
    pass


class InvalidCodeError(Exception):
    pass


def is_expression(code):
    return hasattr(code, "opcode")
#    return isinstance(code, dict) and "opcode" in code


def add_debugging(expression, ctx):
    if ctx:
        expression.line = ctx.start.line
        expression.column = ctx.start.column
    return expression

def new_tuple_op(values, ctx=None):
    if not isinstance(values, (list, tuple)):
        raise InvalidCodeError()
    for value in values:
        if not is_expression(value):
            raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "new_tuple",
        "values": values
    }), ctx)

def new_object_op(properties, ctx=None):
    if not isinstance(properties, dict):
        raise InvalidCodeError()
    for property, expression in properties.items():
        if not isinstance(property, str):
            raise InvalidCodeError()
        if not is_expression(expression):
            raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "new_object",
        "properties": Object(properties)
    }), ctx)


def merge_op(first, second, ctx=None):
    if not is_expression(first) or not is_expression(second):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "merge",
        "first": first,
        "second": second
    }), ctx)


def literal_op(value, ctx=None):
    return add_debugging(Object({
        "opcode": "literal",
        "value": value
    }), ctx)


def type_op(name, ctx=None, **kwargs):
    if not isinstance(name, str):
        raise InvalidCodeError()
    properties = {
        "type": literal_op(name, ctx)
    }
    properties.update(**kwargs)
    return new_object_op(Object(properties), ctx)

def one_of_type(types, ctx=None):
    return type_op(
        "OneOf", ctx, **{
            "types": new_tuple_op(types)
        }
    )

def object_type(properties, ctx=None):
    return type_op(
        "Object", ctx, **{
            "properties": new_object_op(Object({
                property: type for property, type in properties.items()
            }), ctx)
        }
    )

def list_type(entry_types, wildcard_type, ctx=None):
    return type_op(
        "List", ctx, **{
            "entry_types": new_tuple_op(entry_types),
            "wildcard_type": wildcard_type
        }
    )

def function_type(argument, breaks, ctx=None):
    return type_op(
        "Function", ctx, **{
            "argument": argument,
            "breaks": new_object_op(breaks, ctx)
        }
    )

def const_modifier_op(type_expression, ctx=None):
    return Object({
        "opcode": "merge",
        "first": type_expression,
        "second": literal_op({
            "is_const": True
        }, ctx)
    })

def nop():
    return Object({
        "opcode": "nop"
    })


def comma_op(expressions, ctx=None):
    if not isinstance(expressions, list):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "comma",
        "expressions": List(expressions)
    }), ctx)

def loop_op(expression, ctx=None):
    if not is_expression(expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "loop",
        "code": expression
    }), ctx)

def conditional_op(condition, true_code, false_code, ctx=None):
    if not is_expression(condition) or not is_expression(true_code) or not is_expression(false_code):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "conditional",
        "condition": condition,
        "true_code": true_code,
        "false_code": false_code
    }), ctx)

def jump_op(function_expression, argument_expression, ctx=None):
    if not is_expression(function_expression):
        raise InvalidCodeError()
    if argument_expression and not is_expression(argument_expression):
        raise InvalidCodeError()
    code = {
        "opcode": "jump",
        "function": function_expression
    }
    if argument_expression:
        code["argument"] = argument_expression
    return add_debugging(Object(code), ctx)


def transform_op(code_expression, ctx=None, input="value", output="value"):
    if not is_expression(code_expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "transform",
        "code": code_expression,
        "input": input,
        "output": output
    }), ctx)


def break_op(type, value, ctx=None):
    if value is not MISSING and not is_expression(value):
        raise InvalidCodeError()
    code = {
        "opcode": "transform",
        "output": type,
    }
    if value is not MISSING:
        code = spread_dict(code, {
            "code": value,
            "input": "value"
        })
    return add_debugging(Object(code), ctx)


def catch_op(type, code_expression, ctx=None):
    if not is_expression(code_expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "transform",
        "input": type,
        "output": "value",
        "code": code_expression
    }), ctx)

def binary_op(opcode, lvalue, rvalue, ctx=None):
    if not is_expression(lvalue) or not is_expression(rvalue):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": opcode,
        "lvalue": lvalue,
        "rvalue": rvalue
    }), ctx)

def negation_op(expression, ctx=None):
    if not is_expression(expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "negation",
        "expression": expression
    }), ctx)

def not_op(expression, ctx=None):
    if not is_expression(expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "not",
        "expression": expression
    }), ctx)


def assignment_op(dereference, rvalue, ctx=None):
    if not is_expression(dereference) or not is_expression(rvalue):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "assignment",
        "dereference": dereference,
        "rvalue": rvalue
    }), ctx)


def context_op():
    return Object({ "opcode": "context" })


def dereference_op(reference, of, ctx=None):
    if not is_expression(reference) or not is_expression(of):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "dereference",
        "reference": reference,
        "of": of
    }), ctx)


def unbound_dereference_op(reference, ctx=None):
    if not isinstance(reference, str):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "unbound_dereference",
        "reference": reference
    }), ctx)


def symbolic_dereference_ops(parts, ctx=None):
    if not isinstance(parts, list):
        raise ValueError()
    if len(parts) == 1:
        part = parts[0]
        if part in ("local", "argument", "outer"):
            return dereference_op(literal_op(part, ctx), context_op(), ctx)
        else:
            return unbound_dereference_op(part, ctx)
    else:
        return dereference_op(literal_op(parts[-1], ctx), symbolic_dereference_ops(parts[:-1], ctx), ctx)


NO_THROWS = InternalMarker("NO_THROWS")

NO_EXIT = InternalMarker("NO_EXIT")

def prepare_op(function_expression, ctx=None):
    if not is_expression(function_expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "prepare",
        "function": function_expression
    }), ctx)

def import_op(name_expression, ctx=None):
    if not is_expression(name_expression):
        raise InvalidCodeError()
    return add_debugging(Object({
        "opcode": "import",
        "name": name_expression
    }), ctx)


class FunctionStub(object):
    def __init__(
        self,
        code_expressions=MISSING,
        local_variable_types=MISSING,
        local_initializer=MISSING,
        extra_statics=MISSING,
        argument_type_expression=MISSING,
        breaks_types=MISSING
    ):
        self.code_expressions = code_expressions
        self.local_variable_types = local_variable_types
        self.local_initializer = local_initializer
        self.extra_statics = extra_statics
        self.argument_type_expression = argument_type_expression
        self.breaks_types = breaks_types

    def chain(self, other):
        can_merge_functions = True

        if other.argument_type_expression is not MISSING:
            # If the inner function needs an argument, we have no mechanism to provide it
            raise InvalidCodeError()
        if other.breaks_types is not MISSING:
            # The newly created function ignores other.breaks_types, so let's fail early if they're provided
            raise InvalidCodeError()

        if self.local_variable_types is not MISSING and other.local_variable_types is not MISSING:
            # We can only take local variables from one of the two functions
            can_merge_functions = False
        if self.code_expressions is not MISSING and other.local_variable_types is not MISSING:
            # We have code that should execute before the other functions local variables are declared
            can_merge_functions = False
        if self.extra_statics is not MISSING and other.extra_statics is not MISSING:
            # We can only take extra statics from one of the two functions
            can_merge_functions = False
        if self.extra_statics is not MISSING and other.local_variable_types is not MISSING:
            # The inner local_variable_types might reference something from statics
            can_merge_functions = False

        new_code_expressions = None
        our_code_expressions = default(self.code_expressions, MISSING, [])
        other_code_expressions = default(other.code_expressions, MISSING, [])

        if can_merge_functions:
            new_code_expressions = our_code_expressions + other_code_expressions
            local_variable_types = default(self.local_variable_types, MISSING, other.local_variable_types)
            local_initializer = default(self.local_initializer, MISSING, other.local_initializer)
            extra_statics = default(self.extra_statics, MISSING, other.extra_statics)
        else:
            new_code_expressions = our_code_expressions + [ other.create("expression") ]
            local_variable_types = self.local_variable_types
            local_initializer = self.local_initializer
            extra_statics = self.extra_statics

        return FunctionStub(
            code_expressions=new_code_expressions,
            local_variable_types=local_variable_types,
            local_initializer=local_initializer,
            extra_statics=extra_statics,
            argument_type_expression=self.argument_type_expression,
            breaks_types=self.breaks_types
        )

    def requires_function(self):
        return (
            self.argument_type_expression is not MISSING
            or self.local_variable_types is not MISSING
            or self.extra_statics is not MISSING
            or self.breaks_types is not MISSING
        )

    def create(self, output_mode):
        if output_mode not in ("function", "expression"):
            raise FatalException()

        code_expressions = default(self.code_expressions, MISSING, [])

        for c in code_expressions:
            if not isinstance(c, dict):
                raise InvalidCodeError()
            if not is_expression(c):
                raise InvalidCodeError()

        if len(code_expressions) > 0:
            if len(code_expressions) > 1:
                code_expression = comma_op(code_expressions)
            else:
                code_expression = code_expressions[0]
        else:
            code_expression = break_op("return", nop())

        if not self.requires_function() and output_mode == "expression":
            return code_expression

        result = {}

        statics = {}

        if self.argument_type_expression is not MISSING:
            statics["argument"] = self.argument_type_expression
        else:
            statics["argument"] = type_op("Void")

        if self.local_variable_types is not MISSING:
            statics["local"] = object_type(self.local_variable_types)
        else:
            statics["local"] = object_type({})

        if self.local_initializer is not MISSING:
            result["local_initializer"] = self.local_initializer
        else:
            result["local_initializer"] = new_object_op({})

        if self.breaks_types is not MISSING:
            statics["breaks"] = new_object_op(self.breaks_types)
        else:
            statics["breaks"] = new_object_op({ "all": type_op("Inferred") })

        if self.extra_statics is not MISSING:
            statics = spread_dict(self.extra_statics, statics)

        result["static"] = new_object_op(statics)

        if output_mode == "function":
            result["code"] = code_expression
            return Object(result)
        elif output_mode == "expression":
            result["code"] = break_op("function_stub_finished", code_expression)
            return catch_op(
                "function_stub_finished",
                jump_op(prepare_op(literal_op(result)), nop())
            )

class RDHLang4Visitor(langVisitor):

    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop("debug", False)
        langVisitor.__init__(self, *args, **kwargs)

    def visitString(self, ctx):
        return literal_op(ctx.STRING().getText()[1:-1], ctx if self.debug else None)

    def visitNumber(self, ctx):
        return literal_op(int(ctx.NUMBER().getText()), ctx if self.debug else None)

    def visitTrue(self, ctx):
        return literal_op(True, ctx if self.debug else None)

    def visitFalse(self, ctx):
        return literal_op(False, ctx if self.debug else None)

    def visitToFunctionLiteral(self, ctx):
        return prepare_op(literal_op(self.visit(ctx.functionLiteral()), ctx if self.debug else None), ctx if self.debug else None)

    def visitNoParameterFunctionInvocation(self, ctx):
        function_expression = self.visit(ctx.expression())
        return transform_op(jump_op(function_expression, nop(), ctx if self.debug else None), ctx if self.debug else None, "return", "value")

    def visitSingleParameterFunctionInvocation(self, ctx):
        function_expression, argument_expression = ctx.expression()
        function_expression = self.visit(function_expression)
        argument_expression = self.visit(argument_expression)
        return transform_op(jump_op(function_expression, argument_expression, ctx if self.debug else None), ctx if self.debug else None, "return", "value")

    def visitParenthesis(self, ctx):
        return self.visit(ctx.expression())

    def visitAddition(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("addition", lvalue, rvalue, ctx if self.debug else None)

    def visitSubtraction(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("subtraction", lvalue, rvalue, ctx if self.debug else None)

    def visitMakePositive(self, ctx):
        return self.visit(ctx.expression())

    def visitNegation(self, ctx):
        value = self.visit(ctx.expression())
        return negation_op(value, ctx if self.debug else None)

    def visitMultiplication(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("multiplication", lvalue, rvalue, ctx if self.debug else None)

    def visitDivision(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("division", lvalue, rvalue, ctx if self.debug else None)

    def visitModulus(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("modulus", lvalue, rvalue, ctx if self.debug else None)

    def visitGte(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("gte", lvalue, rvalue, ctx if self.debug else None)

    def visitLte(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("lte", lvalue, rvalue, ctx if self.debug else None)

    def visitGt(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("gt", lvalue, rvalue, ctx if self.debug else None)

    def visitLt(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("lt", lvalue, rvalue, ctx if self.debug else None)

    def visitEquals(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return binary_op("equals", lvalue, rvalue, ctx if self.debug else None)

    def visitNotEquals(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return not_op(binary_op("equals", lvalue, rvalue, ctx if self.debug else None))

    def visitNewObject(self, ctx):
        result = {}
        for pair in ctx.pair():
            key, value = self.visit(pair)
            result[key] = value

        return new_object_op(result, ctx if self.debug else None)

    def visitPair(self, ctx):
        if ctx.SYMBOL():
            property = ctx.SYMBOL().getText()
        else:
            property = ctx.STRING().getText()[1:-1]
        return (property, self.visit(ctx.expression()))

    def visitLiteral(self, ctx):
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        if ctx.NUMBER():
            return int(ctx.NUMBER().getText())
        return super(RDHLang4Visitor, self).visitLiteral(ctx)

#     def visitFunctionStub(self, ctx):
#         result = []
#         for statement in ctx.statement():
#             statement = self.visit(statement)
#             if isinstance(statement, list):
#                 result.extend(statement)
#             else:
#                 result.append(statement)
# 
#         for r in result:
#             if r is None:
#                 raise InvalidCodeError()
# 
#         return result

    def visitToFunctionStub(self, ctx):
        function_stub = self.visit(ctx.functionStub())

        code_expressions = default(function_stub.code_expressions, MISSING, [])
        if len(code_expressions) > 0:
            code_expressions[-1] = break_op("return", code_expressions[-1])
        else:
            code_expressions.append(break_op("exit", literal_op(0)))

        return function_stub.create("function")        

    def visitToLiteral(self, ctx):
        return self.visit(ctx.literal())

    def visitSymbolInitialization(self, ctx):
        return (
            ctx.SYMBOL().getText(),
            self.visit(ctx.expression())
        )

    def visitLocalVariableDeclaration(self, ctx):
        type = self.visit(ctx.expression())

        previous_function = ctx.functionStub()
        if previous_function:
            previous_function = self.visit(previous_function)

        for symbol_initialization in reversed(ctx.symbolInitialization()):
            name, initial_value = self.visit(symbol_initialization)

            new_function = FunctionStub(
                local_variable_types={ name: type },
                local_initializer=new_object_op({ name: initial_value })
            )
            if previous_function:
                new_function = new_function.chain(previous_function)
            previous_function = new_function

        return new_function

    def visitStaticValueDeclaration(self, ctx):
        previous_function = self.visit(ctx.functionStub())

        name, value = self.visit(ctx.symbolInitialization())

        return FunctionStub(
            extra_statics={ name: value }
        ).chain(previous_function)

    def visitTypedef(self, ctx):
        previous_function = self.visit(ctx.functionStub())

        value = self.visit(ctx.expression())
        name = ctx.SYMBOL().getText()

        return FunctionStub(
            extra_statics={ name: value },
        ).chain(previous_function)

    def visitImportStatement(self, ctx):
        previous_function = ctx.functionStub()
        if previous_function:
            previous_function = self.visit(previous_function)

        name = ctx.SYMBOL().getText()

        result = FunctionStub(
            extra_statics={ name: import_op(literal_op(name)) },
        )

        if previous_function:
            result = result.chain(previous_function)
        return result

    def visitToExpression(self, ctx):
        code_expressions = [self.visit(e) for e in ctx.expression()]

        new_function = FunctionStub(
            code_expressions=code_expressions
        )

        previous_function = ctx.functionStub()
        if previous_function:
            previous_function = self.visit(previous_function)
            new_function = new_function.chain(previous_function)

        return new_function

    def visitObjectLiteral(self, ctx):
        result = {}
        for literalPair in ctx.literalPair():
            key, value = self.visit(literalPair)
            result[key] = value
        return Object(result)

    def visitLiteralPair(self, ctx):
        if ctx.SYMBOL():
            property = ctx.SYMBOL().getText()
        else:
            property = ctx.STRING().getText()[1:-1]
        return (property, self.visit(ctx.literal()))

    def visitNewTuple(self, ctx):
        expressions = [self.visit(e) for e in ctx.expression()]

        return new_tuple_op(expressions, ctx)

    def visitBoundDereference(self, ctx):
        of = self.visit(ctx.expression())
        reference = ctx.SYMBOL().getText()
        return dereference_op(literal_op(reference, ctx if self.debug else None), of, ctx if self.debug else None)

    def visitDynamicDereference(self, ctx):
        of, reference = ctx.expression()
        of = self.visit(of)
        reference = self.visit(reference)
        return dereference_op(reference, of, ctx if self.debug else None)

    def visitUnboundDereference(self, ctx):
        return symbolic_dereference_ops([ctx.SYMBOL().getText()], ctx if self.debug else None)

    def visitAssignment(self, ctx):
        dereference, expression = ctx.expression()
        dereference = self.visit(dereference)
        expression = self.visit(expression)
        return assignment_op(dereference, expression, ctx if self.debug else None)

    def visitReturnExpression(self, ctx):
        return transform_op(self.visit(ctx.expression()), ctx if self.debug else None, "value", "return")

    def visitExitExpression(self, ctx):
        return transform_op(self.visit(ctx.expression()), ctx if self.debug else None, "value", "exit")

    def visitInferredType(self, ctx):
        return type_op("Inferred", ctx if self.debug else None)

    def visitVoidType(self, ctx):
        return type_op("Void", ctx if self.debug else None)

    def visitIntegerType(self, ctx):
        return type_op("Integer", ctx if self.debug else None)

    def visitStringType(self, ctx):
        return type_op("String", ctx if self.debug else None)

    def visitFunctionType(self, ctx):
        argument, returns = ctx.expression()
        function_exits = ctx.functionExits()
        break_types = {
            "return": self.visit(returns),
        }
        if function_exits is not None:
            function_exits = self.visit(function_exits)
        if function_exits is not NO_EXIT:
            break_types["exit"] = type_op("Integer")
        return function_type(
            self.visit(argument), break_types, ctx if self.debug else None
        )

    def visitAnyType(self, ctx):
        return type_op("Any")

    def visitConstTypeModifier(self, ctx):
        return const_modifier_op(self.visit(ctx.expression()))

    def visitObjectType(self, ctx):
        properties = {
            name: type for type, name in [self.visit(v) for v in ctx.propertyType()]
        }
        return object_type(properties, ctx if self.debug else None)

    def visitListType(self, ctx):
        return list_type(
            [], self.visit(ctx.expression()), ctx if self.debug else None
        )

    def visitTupleType(self, ctx):
        return list_type([
                self.visit(e) for e in ctx.expression()
            ], type_op("Void"), ctx if self.debug else None
        )

    def visitPropertyType(self, ctx):
        return (self.visit(ctx.expression()), ctx.SYMBOL().getText())

    def visitWhileLoop(self, ctx):
        function_stub = self.visit(ctx.functionStub())
        conditional = self.visit(ctx.expression())

        function_stub.code_expressions.insert(
            0, conditional_op(conditional, nop(), break_op("loop_break", MISSING), ctx)
        )

        return catch_op(
            "loop_break",
            loop_op(function_stub.create("expression"))
        )

    def visitIfBlock(self, ctx):
        blocks = ctx.functionStub()

        if len(blocks) == 1:
            true_block, false_block = blocks[0], None
        if len(blocks) == 2:
            true_block, false_block = blocks

        if true_block:
            true_block = self.visit(true_block).create("expression")
        else:
            true_block = nop()
        if false_block:
            false_block = self.visit(false_block).create("expression")
        else:
            false_block = nop()
        conditional = self.visit(ctx.expression())

        return conditional_op(
            conditional,
            true_block,
            false_block,
            ctx
        )

    def visitExecute(self, ctx):
        code = self.visit(ctx.literal())
        return add_debugging(code, ctx)

    def visitFunctionLiteral(self, ctx):
        argument_type, return_type = self.visit(ctx.functionArgumentAndReturns())

        function_throws = ctx.functionThrows()
        if function_throws is None:
            function_throws = type_op("Inferred")
        else:
            function_throws = self.visit(function_throws)

        function_exits = ctx.functionExits()
        if function_exits is None:
            function_exits = type_op("Integer")
        else:
            function_exits = self.visit(function_exits)

        breaks = {
            "return": return_type
        }

        if function_throws is not NO_THROWS:
            breaks["exception"] = function_throws
        if function_exits is not NO_EXIT:
            breaks["exit"] = function_exits

        our_function = FunctionStub(
            argument_type_expression=argument_type, breaks_types=breaks
        )

        remainder_function = ctx.functionStub()
        if remainder_function:
            remainder_function = self.visit(remainder_function)
            our_function = our_function.chain(remainder_function)

        return our_function.create("function")

    def visitFunctionArgumentAndReturns(self, ctx):
        possible_argument_and_return_type = ctx.expression()

        if len(possible_argument_and_return_type) == 2:
            argument_type, return_type = possible_argument_and_return_type
            argument_type = self.visit(argument_type)
            return_type = self.visit(return_type)
        elif len(possible_argument_and_return_type) == 1:
            argument_type = self.visit(possible_argument_and_return_type[0])
            return_type = type_op("Inferred")
        else:
            argument_type = type_op("Void") #one_of_type([ type_op("Void"), type_op("Any") ])
            return_type = type_op("Inferred")

        return (argument_type, return_type)

    def visitFunctionThrows(self, ctx):
        if ctx.expression():
            return self.visit(ctx.expression())
        else:
            return NO_THROWS

    def visitFunctionExits(self, ctx):
        return NO_EXIT
