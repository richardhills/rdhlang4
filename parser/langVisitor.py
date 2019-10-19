# Generated from lang.g4 by ANTLR 4.7.2
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by langParser.

class langVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by langParser#code.
    def visitCode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#newObject.
    def visitNewObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#pair.
    def visitPair(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#literal.
    def visitLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#objectLiteral.
    def visitObjectLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#literalPair.
    def visitLiteralPair(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#array.
    def visitArray(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#noParameterFunctionInvocation.
    def visitNoParameterFunctionInvocation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#unboundDereference.
    def visitUnboundDereference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#string.
    def visitString(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toObjectType.
    def visitToObjectType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toFunctionLiteral.
    def visitToFunctionLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#false.
    def visitFalse(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toFunctionType.
    def visitToFunctionType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toVoidType.
    def visitToVoidType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toAnyType.
    def visitToAnyType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toNewObject.
    def visitToNewObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#boundDereference.
    def visitBoundDereference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#number.
    def visitNumber(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toStringType.
    def visitToStringType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toIntegerType.
    def visitToIntegerType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#singleParameterFunctionInvocation.
    def visitSingleParameterFunctionInvocation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#null.
    def visitNull(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toInferredType.
    def visitToInferredType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toArray.
    def visitToArray(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#true.
    def visitTrue(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toReturnExpression.
    def visitToReturnExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#multiplication.
    def visitMultiplication(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#addition.
    def visitAddition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#localVariableDeclaration.
    def visitLocalVariableDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#staticValueDeclaration.
    def visitStaticValueDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#typedef.
    def visitTypedef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toExpression.
    def visitToExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#voidType.
    def visitVoidType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#inferredType.
    def visitInferredType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#integerType.
    def visitIntegerType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#stringType.
    def visitStringType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionType.
    def visitFunctionType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#objectType.
    def visitObjectType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#anyType.
    def visitAnyType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#propertyType.
    def visitPropertyType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionLiteral.
    def visitFunctionLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionArgumentAndReturns.
    def visitFunctionArgumentAndReturns(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionThrows.
    def visitFunctionThrows(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#returnExpression.
    def visitReturnExpression(self, ctx):
        return self.visitChildren(ctx)


