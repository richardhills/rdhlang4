# Generated from lang.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .langParser import langParser
else:
    from langParser import langParser

# This class defines a complete generic visitor for a parse tree produced by langParser.

class langVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by langParser#toLiteral.
    def visitToLiteral(self, ctx:langParser.ToLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toFunctionStub.
    def visitToFunctionStub(self, ctx:langParser.ToFunctionStubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#localVariableDeclaration.
    def visitLocalVariableDeclaration(self, ctx:langParser.LocalVariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#staticValueDeclaration.
    def visitStaticValueDeclaration(self, ctx:langParser.StaticValueDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#typedef.
    def visitTypedef(self, ctx:langParser.TypedefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#importStatement.
    def visitImportStatement(self, ctx:langParser.ImportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toExpression.
    def visitToExpression(self, ctx:langParser.ToExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#symbolInitialization.
    def visitSymbolInitialization(self, ctx:langParser.SymbolInitializationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#newObject.
    def visitNewObject(self, ctx:langParser.NewObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#pair.
    def visitPair(self, ctx:langParser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#literal.
    def visitLiteral(self, ctx:langParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#objectLiteral.
    def visitObjectLiteral(self, ctx:langParser.ObjectLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#literalPair.
    def visitLiteralPair(self, ctx:langParser.LiteralPairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#array.
    def visitArray(self, ctx:langParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#string.
    def visitString(self, ctx:langParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toExitExpression.
    def visitToExitExpression(self, ctx:langParser.ToExitExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toFunctionType.
    def visitToFunctionType(self, ctx:langParser.ToFunctionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toVoidType.
    def visitToVoidType(self, ctx:langParser.ToVoidTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toIf.
    def visitToIf(self, ctx:langParser.ToIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toNewObject.
    def visitToNewObject(self, ctx:langParser.ToNewObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#division.
    def visitDivision(self, ctx:langParser.DivisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#boundDereference.
    def visitBoundDereference(self, ctx:langParser.BoundDereferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#number.
    def visitNumber(self, ctx:langParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toWhileLoop.
    def visitToWhileLoop(self, ctx:langParser.ToWhileLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toArray.
    def visitToArray(self, ctx:langParser.ToArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toReturnExpression.
    def visitToReturnExpression(self, ctx:langParser.ToReturnExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#gte.
    def visitGte(self, ctx:langParser.GteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#multiplication.
    def visitMultiplication(self, ctx:langParser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#lte.
    def visitLte(self, ctx:langParser.LteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#modulus.
    def visitModulus(self, ctx:langParser.ModulusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#addition.
    def visitAddition(self, ctx:langParser.AdditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#noParameterFunctionInvocation.
    def visitNoParameterFunctionInvocation(self, ctx:langParser.NoParameterFunctionInvocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#unboundDereference.
    def visitUnboundDereference(self, ctx:langParser.UnboundDereferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toObjectType.
    def visitToObjectType(self, ctx:langParser.ToObjectTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toFunctionLiteral.
    def visitToFunctionLiteral(self, ctx:langParser.ToFunctionLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#assignment.
    def visitAssignment(self, ctx:langParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#false.
    def visitFalse(self, ctx:langParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toAnyType.
    def visitToAnyType(self, ctx:langParser.ToAnyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toStringType.
    def visitToStringType(self, ctx:langParser.ToStringTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toIntegerType.
    def visitToIntegerType(self, ctx:langParser.ToIntegerTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#singleParameterFunctionInvocation.
    def visitSingleParameterFunctionInvocation(self, ctx:langParser.SingleParameterFunctionInvocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#null.
    def visitNull(self, ctx:langParser.NullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#toInferredType.
    def visitToInferredType(self, ctx:langParser.ToInferredTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#equals.
    def visitEquals(self, ctx:langParser.EqualsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#true.
    def visitTrue(self, ctx:langParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#notEquals.
    def visitNotEquals(self, ctx:langParser.NotEqualsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#voidType.
    def visitVoidType(self, ctx:langParser.VoidTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#inferredType.
    def visitInferredType(self, ctx:langParser.InferredTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#integerType.
    def visitIntegerType(self, ctx:langParser.IntegerTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#stringType.
    def visitStringType(self, ctx:langParser.StringTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionType.
    def visitFunctionType(self, ctx:langParser.FunctionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#objectType.
    def visitObjectType(self, ctx:langParser.ObjectTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#anyType.
    def visitAnyType(self, ctx:langParser.AnyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#propertyType.
    def visitPropertyType(self, ctx:langParser.PropertyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#whileLoop.
    def visitWhileLoop(self, ctx:langParser.WhileLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#ifBlock.
    def visitIfBlock(self, ctx:langParser.IfBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionLiteral.
    def visitFunctionLiteral(self, ctx:langParser.FunctionLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionArgumentAndReturns.
    def visitFunctionArgumentAndReturns(self, ctx:langParser.FunctionArgumentAndReturnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionThrows.
    def visitFunctionThrows(self, ctx:langParser.FunctionThrowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#functionExits.
    def visitFunctionExits(self, ctx:langParser.FunctionExitsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#returnExpression.
    def visitReturnExpression(self, ctx:langParser.ReturnExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by langParser#exitExpression.
    def visitExitExpression(self, ctx:langParser.ExitExpressionContext):
        return self.visitChildren(ctx)



del langParser