# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from langLexer import langLexer
from langParser import langParser
from langVisitor import langVisitor

class OpcodeExpression(object):
    def __init__(self, data):
        self.data = data

def wrap_in_literal_opcode_if_needed(data_or_opcode):
    if isinstance(data_or_opcode, OpcodeExpression):
        return data_or_opcode.data
    else:
        return {
            "opcode": "literal",
            "value": data_or_opcode
        }

class RDHLang4Visitor(langVisitor):
    def visitObj(self, ctx):
        n = ctx.getChildCount()
        result = {}
        for i in range(1, n - 1, 2):
            key, value = self.visitPair(ctx.getChild(i))
            result[key] = value
        if any([isinstance(r, OpcodeExpression) for r in result.values()]):
            result = OpcodeExpression({
                "opcode": "object_template",
                "properties": {
                    key: wrap_in_literal_opcode_if_needed(value) for key, value in result.iteritems()
                }
            })
        return result

    def visitArray(self, ctx):
        n = ctx.getChildCount()
        result = []
        for i in range(1, n - 1):
            result.append(self.visitValue(ctx.getChild(i)))
        if any([isinstance(r, OpcodeExpression) for r in result]):
            result = OpcodeExpression({
                "opcode": "array_template",
                "elements": {
                    wrap_in_literal_opcode_if_needed(value) for value in result
                }
            })
        return result

    def visitPair(self, ctx):
        return (ctx.STRING().getText()[1:-1], self.visitExpression(ctx.expression()))

    def visitExpression(self, ctx):
        if ctx.STRING() != None:
            return ctx.STRING().getText()[1:-1]
        if ctx.NUMBER() != None:
            return float(ctx.NUMBER().getText())
        else:
            return super(RDHLang4Visitor, self).visitExpression(ctx)

    def visitAssignment(self, ctx):
        dereference, _, expression = ctx.children
        dereference = self.visitDereference(dereference)
        expression = self.visitExpression(expression)
        return OpcodeExpression({
            "opcode": "assignment",
            "lvalue": wrap_in_literal_opcode_if_needed(dereference),
            "rvalue": wrap_in_literal_opcode_if_needed(expression)
        })

    def visitDereference(self, ctx):
        of = reference = None
        if ctx.getChildCount() == 3:
            of, _, reference = ctx.children
            of = wrap_in_literal_opcode_if_needed(
                self.visitDereference(of)
            )
        else:
            reference, = ctx.children
            of = {
                "opcode": "dereference",
                "reference": {
                    "opcode": "literal",
                    "value": "compound"
                }
            }
        reference = reference.getText()
        reference = wrap_in_literal_opcode_if_needed(reference)
        return OpcodeExpression({
            "opcode": "dereference",
            "of": of,
            "reference": reference
        })

    def visitReturn(self, ctx):
        _, _, expression = ctx.children
        return OpcodeExpression({
            "opcode": "break",
            "type": "return",
            "value": expression
        })

    def visitFunctionInstantiation(self, ctx):
        n = ctx.getChildCount()
        expressions = []
        for i in range(4, n-1, 2):
            expressions.append(
                wrap_in_literal_opcode_if_needed(
                    self.visitExpression(ctx.getChild(i))
                )
            )

        return {
            "statics": {
                "opcode": "literal",
                "value": {}
            },
            "code": {
                "opcode": "comma",
                "expressions": expressions
            }
        }

    def visitMethodInstantiation(self, ctx):
        _, obj = ctx.children
        obj = self.visitObj(obj)

        return {
            "statics": obj["statics"],
            "code": obj["code"]
        }
