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


    # Visit a parse tree produced by langParser#otherExpressions.
    def visitOtherExpressions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toOtherExpressions.
    def visitToOtherExpressions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#addition.
    def visitAddition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#localVariableDeclaration.
    def visitLocalVariableDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toExpression.
    def visitToExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#voidType.
    def visitVoidType(self, ctx):
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


    # Visit a parse tree produced by langParser#functionLiteral.
    def visitFunctionLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionLiteralWithTypes.
    def visitFunctionLiteralWithTypes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionLiteralWithoutTypes.
    def visitFunctionLiteralWithoutTypes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#returnExpression.
    def visitReturnExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#dereference.
    def visitDereference(self, ctx):
        return self.visitChildren(ctx)


