# Generated from lang.g4 by ANTLR 4.7.2
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by langParser.

class langVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by langParser#code.
    def visitCode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#obj.
    def visitObj(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#pair.
    def visitPair(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#array.
    def visitArray(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionInstantiation.
    def visitFunctionInstantiation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#methodInstantiation.
    def visitMethodInstantiation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#dereference.
    def visitDereference(self, ctx):
        return self.visitChildren(ctx)


