# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from cookielib import offset_from_tz_string
from symbol import argument

from antlr4.tree.Tree import TerminalNodeImpl

from parser.langVisitor import langVisitor
from utils import spread_dict


class ParseError(Exception):
    pass


class InvalidCodeError(Exception):
    pass


def is_expression(code):
    return isinstance(code, dict) and "opcode" in code


def new_object_op(properties):
    if not isinstance(properties, dict):
        raise InvalidCodeError()
    for property, expression in properties.items():
        if not isinstance(property, basestring):
            raise InvalidCodeError()
        if not is_expression(expression):
            raise InvalidCodeError()
    return {
        "opcode": "new_object",
        "properties": properties
    }


def merge_op(first, second):
    if not is_expression(first) or not is_expression(second):
        raise InvalidCodeError()
    return {
        "opcode": "merge",
        "first": first,
        "second": second
    }


def literal_op(value):
    return {
        "opcode": "literal",
        "value": value
    }


def type(name, **kwargs):
    if not isinstance(name, basestring):
        raise InvalidCodeError()
    properties = {
        "type": literal_op(name)
    }
    properties.update(**kwargs)
    return new_object_op(properties)


def object_type(properties):
    return type(
        "Object", **{
            "properties": new_object_op({
                property: type for property, type in properties.items()
            })
        }
    )


def function_type(argument, breaks):
    return type(
        "Function", **{
            "argument": argument,
            "breaks": new_object_op(breaks)
        }
    )


def nop():
    return {
        "opcode": "nop"
    }


def comma_op(expressions):
    if not isinstance(expressions, list):
        raise InvalidCodeError()
    return {
        "opcode": "comma",
        "expressions": expressions
    }

def invoke_ops(function_expression, argument_expression):
    return catch_op("return", jump_op(function_expression, argument_expression))


def jump_op(function_expression, argument_expression):
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
    return code

def break_op(type, value):
    if not is_expression(value):
        raise InvalidCodeError()
    return {
        "opcode": "break",
        "type": type,
        "value": value
    }

def catch_op(type, code_expression):
    if not is_expression(code_expression):
        raise InvalidCodeError()
    return {
        "opcode": "catch",
        "type": type,
        "code": code_expression
    }


def addition_op(lvalue, rvalue):
    if not is_expression(lvalue) or not is_expression(rvalue):
        raise InvalidCodeError()
    return {
        "opcode": "add",
        "lvalue": lvalue,
        "rvalue": rvalue
    }


def assignment_op(dereference, rvalue):
    if not is_expression(dereference) or not is_expression(rvalue):
        raise InvalidCodeError()
    return {
        "opcode": "assignment",
        "dereference": dereference,
        "rvalue": rvalue
    }


def dereference_op(*parts):
    reference = parts[-1]

    if len(parts) > 1:
        of = dereference_op(*parts[:-1])
        return {
            "opcode": "dereference",
            "reference": reference,
            "of": of
        }
    else:
        return {
            "opcode": "unbound_dereference",
            "reference": reference
        }

def function(
    argument_type_expression,
    breaks_type_expression,
    code_expressions
):
    sub_code_block = []

    local_declarations = [c for c in code_expressions if isinstance(c, LocalVariableDeclaration)]
    local_initializer = new_object_op({})

    for index, code_expression in enumerate(reversed(code_expressions)):
        if not isinstance(code_expression, LocalVariableDeclaration):
            sub_code_block.insert(0, code_expression)
        else:
            local_variable_declaration = new_object_op({
                code_expression.name: code_expression.initial_value
            })

            remaining_local_declarations = [d for d in local_declarations if d != code_expression]
            remaining_code = code_expressions[0 : len(code_expressions) - index - 1]

            if len(remaining_code) > 0:
                remaining_code = remaining_code + [
                    break_op("local_initialized", dereference_op("local"))
                ]

                function_for_remaining_code = literal_op(function(
                    type("Void"), merge_op(breaks_type_expression, new_object_op({
                        "local_initialized": object_type({
                            d.name: d.type for d in remaining_local_declarations
                        })
                    })), remaining_code
                ))
                local_initializer = merge_op(
                    catch_op("local_initialized", jump_op(prepare_op(function_for_remaining_code), None)),
                    local_variable_declaration
                )
            else:
                local_initializer = local_variable_declaration
            # We've got enough now to create the function
            break

    local_type_expression =  object_type({
        local_declaration.name: local_declaration.type for local_declaration in local_declarations
    })

    return function_literal(
        argument_type_expression,
        breaks_type_expression,
        local_type_expression,
        local_initializer,
        sub_code_block
    )

def function_literal(argument_type_expression, breaks_type_expression, local_type_expression, local_initializer, code_expressions):
    function_literal = {
        "static": new_object_op({
            "breaks": breaks_type_expression,
            "local": local_type_expression,
            "argument": argument_type_expression
        })
    }

    if local_initializer:
        function_literal["local_initializer"] = local_initializer

    if len(code_expressions) > 0:
        if len(code_expressions) > 1:
            function_literal["code"] = comma_op(code_expressions)
        else:
            function_literal["code"] = code_expressions[0]

    return function_literal

def prepare_op(function_expression):
    if not is_expression(function_expression):
        raise InvalidCodeError()
    return {
        "opcode": "prepare",
        "function": function_expression
    }


class LocalVariableDeclaration(object):

    def __init__(self, type, name, initial_value):
        self.type = type
        self.name = name
        if not is_expression(initial_value):
            raise InvalidCodeError()
        self.initial_value = initial_value


class RDHLang4Visitor(langVisitor):

    def visitLocalVariableDeclaration(self, ctx):
        type, initialValue = ctx.expression()
        type = self.visit(type)
        initialValue = self.visit(initialValue)
        name = ctx.SYMBOL().getText()
        return LocalVariableDeclaration(type, name, initialValue)

    def visitOtherExpressions(self, ctx):
        if ctx.STRING():
            return literal_op(ctx.STRING().getText()[1:-1])
        if ctx.NUMBER():
            return literal_op(int(ctx.NUMBER().getText()))
        return super(RDHLang4Visitor, self).visitOtherExpressions(ctx)

    def visitAddition(self, ctx):
        return addition_op(
            self.visit(ctx.additionSubtractionAndOtherExpressions()),
            self.visit(ctx.otherExpressions()),
        )

    def visitNewObject(self, ctx):
        result = {}
        for pair in ctx.pair():
            key, value = self.visit(pair)
            result[key] = value

        return new_object_op(result)

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

    def visitAssignment(self, ctx):
        dereference = self.visit(ctx.dereference())
        expression = self.visit(ctx.expression())
        return assignment_op(dereference, expression)

    def visitDereference(self, ctx):
        reference = ctx.SYMBOL()[0].getText()
        if ctx.expression():
            of = self.visit(ctx.expression())
            return dereference_op(of, literal_op(reference))
        else:
            return dereference_op(reference)

    def visitReturnExpression(self, ctx):
        return break_op("return", self.visit(ctx.expression()))

    def visitVoidType(self, ctx):
        return type("Void")

    def visitIntegerType(self, ctx):
        return type("Integer")

    def visitStringType(self, ctx):
        return type("String")

    def visitFunctionType(self, ctx):
        argument, returns = ctx.expression()
        return function_type(
            self.visit(argument), {
                "returns": { self.visit(returns) }
            }
        )

    def visitFunctionLiteralWithoutTypes(self, ctx):
        void_type = type("Void")
        code_statements = [self.visit(e) for e in ctx.statement()]
        return function(
            void_type, new_object_op({ "return": void_type }), code_statements
        )

    def visitFunctionLiteralWithTypes(self, ctx):
        argument_type, return_type = ctx.expression()
        argument_type = self.visit(argument_type)
        return_type = self.visit(return_type)
        code_statements = [self.visit(e) for e in ctx.statement()]

        return function(
            argument_type, new_object_op({ "return": return_type }), code_statements
        )
