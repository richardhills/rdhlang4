# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from cookielib import offset_from_tz_string
from symbol import argument

from antlr4.tree.Tree import TerminalNodeImpl

from parser.langVisitor import langVisitor
from utils import spread_dict, MISSING


class ParseError(Exception):
    pass


class InvalidCodeError(Exception):
    pass


def is_expression(code):
    return isinstance(code, dict) and "opcode" in code


def add_debugging(expression, ctx):
    if ctx:
        expression["line"] = ctx.start.line
        expression["column"] = ctx.start.column
    return expression

def new_object_op(properties, ctx=None):
    if not isinstance(properties, dict):
        raise InvalidCodeError()
    for property, expression in properties.items():
        if not isinstance(property, basestring):
            raise InvalidCodeError()
        if not is_expression(expression):
            raise InvalidCodeError()
    return add_debugging({
        "opcode": "new_object",
        "properties": properties
    }, ctx)


def merge_op(first, second, ctx=None):
    if not is_expression(first) or not is_expression(second):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "merge",
        "first": first,
        "second": second
    }, ctx)


def literal_op(value, ctx=None):
    return add_debugging({
        "opcode": "literal",
        "value": value
    }, ctx)


def type(name, ctx=None, **kwargs):
    if not isinstance(name, basestring):
        raise InvalidCodeError()
    properties = {
        "type": literal_op(name, ctx)
    }
    properties.update(**kwargs)
    return new_object_op(properties, ctx)


def object_type(properties, ctx=None):
    return type(
        "Object", ctx, **{
            "properties": new_object_op({
                property: type for property, type in properties.items()
            }, ctx)
        }
    )


def function_type(argument, breaks, ctx=None):
    return type(
        "Function", ctx, **{
            "argument": argument,
            "breaks": new_object_op(breaks, ctx)
        }
    )


def nop():
    return {
        "opcode": "nop"
    }


def comma_op(expressions, ctx=None):
    if not isinstance(expressions, list):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "comma",
        "expressions": expressions
    }, ctx)


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
    return add_debugging(code, ctx)

def transform_op(code_expression, ctx=None, input="value", output="value"):
    if not is_expression(code_expression):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "transform",
        "code": code_expression,
        "input": input,
        "output": output
    }, ctx)

def break_op(type, value, ctx=None):
    if not is_expression(value):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "transform",
        "input": "value",
        "output": type,
        "code": value
    }, ctx)


def catch_op(type, code_expression, ctx=None):
    if not is_expression(code_expression):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "transform",
        "input": type,
        "output": "value",
        "code": code_expression
    }, ctx)


def addition_op(lvalue, rvalue, ctx=None):
    if not is_expression(lvalue) or not is_expression(rvalue):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "addition",
        "lvalue": lvalue,
        "rvalue": rvalue
    }, ctx)

def multiplication_op(lvalue, rvalue, ctx=None):
    if not is_expression(lvalue) or not is_expression(rvalue):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "multiplication",
        "lvalue": lvalue,
        "rvalue": rvalue,
    }, ctx)

def assignment_op(dereference, rvalue, ctx=None):
    if not is_expression(dereference) or not is_expression(rvalue):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "assignment",
        "dereference": dereference,
        "rvalue": rvalue
    }, ctx)

def context_op():
    return { "opcode": "context" }

def dereference_op(reference, of, ctx=None):
    if not is_expression(reference) or not is_expression(of):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "dereference",
        "reference": reference,
        "of": of
    }, ctx)

def unbound_dereference_op(reference, ctx=None):
    if not isinstance(reference, basestring):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "unbound_dereference",
        "reference": reference
    }, ctx)

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

def function_literal(argument_type_expression, breaks_type_expression, local_type_expression, local_initializer, code_expressions, ctx=None):
    function_literal = {
        "static": new_object_op({
            "breaks": breaks_type_expression,
            "local": local_type_expression,
            "argument": argument_type_expression
        }, ctx)
    }

    if local_initializer:
        function_literal["local_initializer"] = local_initializer

    for c in code_expressions:
        if not isinstance(c, dict):
            raise InvalidCodeError()
        if not is_expression(c):
            raise InvalidCodeError()

    if len(code_expressions) > 0:
        if len(code_expressions) > 1:
            function_literal["code"] = comma_op(code_expressions, ctx)
        else:
            function_literal["code"] = code_expressions[0]

    return function_literal


def prepare_op(function_expression, ctx=None):
    if not is_expression(function_expression):
        raise InvalidCodeError()
    return add_debugging({
        "opcode": "prepare",
        "function": function_expression
    }, ctx)

class LocalVariableDeclaration(object):

    def __init__(self, type, name, initial_value):
        self.type = type
        self.name = name
        if not is_expression(initial_value):
            raise InvalidCodeError()
        self.initial_value = initial_value


class RDHLang4Visitor(langVisitor):
    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop("debug", False)
        langVisitor.__init__(self, *args, **kwargs)

    def visitLocalVariableDeclaration(self, ctx):
        type, initialValue = ctx.expression()
        type = self.visit(type)
        initialValue = self.visit(initialValue)
        name = ctx.SYMBOL().getText()
        return LocalVariableDeclaration(type, name, initialValue)

    def visitString(self, ctx):
        return literal_op(ctx.STRING().getText()[1:-1], ctx if self.debug else None)

    def visitNumber(self, ctx):
        return literal_op(int(ctx.NUMBER().getText()), ctx if self.debug else None)

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

    def visitAddition(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return addition_op(lvalue, rvalue, ctx if self.debug else None)

    def visitMultiplication(self, ctx):
        lvalue, rvalue = ctx.expression()
        lvalue = self.visit(lvalue)
        rvalue = self.visit(rvalue)
        return multiplication_op(lvalue, rvalue, ctx if self.debug else None)

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

    def visitObjectLiteral(self, ctx):
        result = {}
        for literalPair in ctx.literalPair():
            key, value = self.visit(literalPair)
            result[key] = value
        return result

    def visitLiteralPair(self, ctx):
        if ctx.SYMBOL():
            property = ctx.SYMBOL().getText()
        else:
            property = ctx.STRING().getText()[1:-1]
        return (property, self.visit(ctx.literal()))

    def visitArray(self, ctx):
        raise ValueError()
# 
#         n = ctx.getChildCount()
#         result = []
#         for i in range(1, n - 1):
#             result.append(self.visitValue(ctx.getChild(i)))
#         if any([isinstance(r, OpcodeExpression) for r in result]):
#             result = OpcodeExpression({
#                 "opcode": "array_template",
#                 "elements": {
#                     ensure_data_is_opcode(value) for value in result
#                 }
#             })
#         return result

    def visitBoundDereference(self, ctx):
        of = self.visit(ctx.expression())
        reference = ctx.SYMBOL().getText()
        return dereference_op(literal_op(reference, ctx if self.debug else None), of, ctx if self.debug else None)
    
    def visitUnboundDereference(self, ctx):
        return symbolic_dereference_ops([ctx.SYMBOL().getText()], ctx if self.debug else None)

    def visitAssignment(self, ctx):
        dereference, expression = ctx.expression()
        dereference = self.visit(dereference)
        expression = self.visit(expression)
        return assignment_op(dereference, expression, ctx if self.debug else None)

    def visitReturnExpression(self, ctx):
        return transform_op(self.visit(ctx.expression()), ctx if self.debug else None, "value", "return")

    def visitVoidType(self, ctx):
        return type("Void", ctx if self.debug else None)

    def visitIntegerType(self, ctx):
        return type("Integer", ctx if self.debug else None)

    def visitStringType(self, ctx):
        return type("String", ctx if self.debug else None)

    def visitFunctionType(self, ctx):
        argument, returns = ctx.expression()
        return function_type(
            self.visit(argument), {
                "return": self.visit(returns)
            }, ctx if self.debug else None
        )

    def visitAnyType(self, ctx):
        return type("Any")

    def visitObjectType(self, ctx):
        properties = {
            name: type for type, name in [self.visit(v) for v in ctx.propertyType()]
        }
        return object_type(properties, ctx if self.debug else None)

    def visitPropertyType(self, ctx):
        return (self.visit(ctx.expression()), ctx.SYMBOL().getText())

    def visit_function(
        self,
        argument_type_expression,
        breaks_type_expression,
        local_variable_types,
        local_initializer,
        code_expressions,
        ctx
    ):
        code_for_us = []
        local_variable_declaration = None
        code_for_remainder_function = None

        for index, code_expression_ctx in enumerate(code_expressions):
            code_expression = self.visit(code_expression_ctx)
            if not isinstance(code_expression, LocalVariableDeclaration):
                code_for_us.append(code_expression)
            else:
                local_variable_declaration = code_expression
                code_for_remainder_function = code_expressions[index + 1:]
                break

        need_remainder_function = local_variable_declaration is not None
        need_function_for_us = len(code_for_us) > 0 or not need_remainder_function or len(local_variable_types) > 0

        if need_remainder_function:
            remainder_function_local_variable_types = spread_dict(local_variable_types, {
                local_variable_declaration.name: local_variable_declaration.type
            })

            new_variable_initializer = new_object_op({
                local_variable_declaration.name: local_variable_declaration.initial_value
            }, ctx if self.debug else None)

            if len(local_variable_types) > 0:
                remainder_function_local_variable_initializer = merge_op(
                    symbolic_dereference_ops(["outer", "local"], ctx if self.debug else None),
                    new_variable_initializer, ctx if self.debug else None
                )
            else:
                remainder_function_local_variable_initializer = new_variable_initializer

            if need_function_for_us:
                remainder_function = self.visit_function(
                    type("Void", ctx if self.debug else None),
                    breaks_type_expression,
                    remainder_function_local_variable_types,
                    remainder_function_local_variable_initializer,
                    code_for_remainder_function,
                    ctx
                )

                code_for_us.append(
                    jump_op(prepare_op(literal_op(remainder_function, ctx), ctx), nop(), ctx)
                )
            else:
                remaining_code_function = self.visit_function(
                    argument_type_expression,
                    breaks_type_expression,
                    remainder_function_local_variable_types,
                    remainder_function_local_variable_initializer,
                    code_for_remainder_function,
                    ctx if self.debug else None
                )

        if need_function_for_us:
            return function_literal(
                argument_type_expression,
                breaks_type_expression,
                object_type(local_variable_types, ctx if self.debug else None),
                local_initializer,
                code_for_us,
                ctx if self.debug else None
            )
        else:
            return remaining_code_function

    def visitFunctionLiteral(self, ctx):
        argument_type, return_type = self.visit(ctx.functionArgumentAndReturns())
        function_throws = ctx.functionThrows()

        if function_throws is None:
            function_throws = type("Inferred")
        else:
            function_throws = self.visit(function_throws)
            if function_throws is MISSING:
                function_throws = None

        breaks = {
            "return": return_type
        }
        if function_throws:
            breaks["exception"] = function_throws

        return self.visit_function(
            argument_type,
            new_object_op(breaks),
            {},
            new_object_op({}, ctx if self.debug else None),
            ctx.statement(),
            ctx if self.debug else None
        )

    def visitFunctionArgumentAndReturns(self, ctx):
        possible_argument_and_return_type = ctx.expression()

        if len(possible_argument_and_return_type) == 2:
            argument_type, return_type = possible_argument_and_return_type
            argument_type = self.visit(argument_type)
            return_type = self.visit(return_type)
        else:
            argument_type = type("Void")
            return_type = type("Void")

        return (argument_type, return_type)

    def visitFunctionThrows(self, ctx):
        if ctx.expression():
            return self.visit(ctx.expression())
        else:
            return MISSING
