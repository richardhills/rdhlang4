# Generated from lang.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .langParser import langParser
else:
    from langParser import langParser

# This class defines a complete listener for a parse tree produced by langParser.
class langListener(ParseTreeListener):

    # Enter a parse tree produced by langParser#toLiteral.
    def enterToLiteral(self, ctx:langParser.ToLiteralContext):
        pass

    # Exit a parse tree produced by langParser#toLiteral.
    def exitToLiteral(self, ctx:langParser.ToLiteralContext):
        pass


    # Enter a parse tree produced by langParser#toFunctionStub.
    def enterToFunctionStub(self, ctx:langParser.ToFunctionStubContext):
        pass

    # Exit a parse tree produced by langParser#toFunctionStub.
    def exitToFunctionStub(self, ctx:langParser.ToFunctionStubContext):
        pass


    # Enter a parse tree produced by langParser#localVariableDeclaration.
    def enterLocalVariableDeclaration(self, ctx:langParser.LocalVariableDeclarationContext):
        pass

    # Exit a parse tree produced by langParser#localVariableDeclaration.
    def exitLocalVariableDeclaration(self, ctx:langParser.LocalVariableDeclarationContext):
        pass


    # Enter a parse tree produced by langParser#staticValueDeclaration.
    def enterStaticValueDeclaration(self, ctx:langParser.StaticValueDeclarationContext):
        pass

    # Exit a parse tree produced by langParser#staticValueDeclaration.
    def exitStaticValueDeclaration(self, ctx:langParser.StaticValueDeclarationContext):
        pass


    # Enter a parse tree produced by langParser#typedef.
    def enterTypedef(self, ctx:langParser.TypedefContext):
        pass

    # Exit a parse tree produced by langParser#typedef.
    def exitTypedef(self, ctx:langParser.TypedefContext):
        pass


    # Enter a parse tree produced by langParser#importStatement.
    def enterImportStatement(self, ctx:langParser.ImportStatementContext):
        pass

    # Exit a parse tree produced by langParser#importStatement.
    def exitImportStatement(self, ctx:langParser.ImportStatementContext):
        pass


    # Enter a parse tree produced by langParser#toExpression.
    def enterToExpression(self, ctx:langParser.ToExpressionContext):
        pass

    # Exit a parse tree produced by langParser#toExpression.
    def exitToExpression(self, ctx:langParser.ToExpressionContext):
        pass


    # Enter a parse tree produced by langParser#symbolInitialization.
    def enterSymbolInitialization(self, ctx:langParser.SymbolInitializationContext):
        pass

    # Exit a parse tree produced by langParser#symbolInitialization.
    def exitSymbolInitialization(self, ctx:langParser.SymbolInitializationContext):
        pass


    # Enter a parse tree produced by langParser#newObject.
    def enterNewObject(self, ctx:langParser.NewObjectContext):
        pass

    # Exit a parse tree produced by langParser#newObject.
    def exitNewObject(self, ctx:langParser.NewObjectContext):
        pass


    # Enter a parse tree produced by langParser#pair.
    def enterPair(self, ctx:langParser.PairContext):
        pass

    # Exit a parse tree produced by langParser#pair.
    def exitPair(self, ctx:langParser.PairContext):
        pass


    # Enter a parse tree produced by langParser#literal.
    def enterLiteral(self, ctx:langParser.LiteralContext):
        pass

    # Exit a parse tree produced by langParser#literal.
    def exitLiteral(self, ctx:langParser.LiteralContext):
        pass


    # Enter a parse tree produced by langParser#objectLiteral.
    def enterObjectLiteral(self, ctx:langParser.ObjectLiteralContext):
        pass

    # Exit a parse tree produced by langParser#objectLiteral.
    def exitObjectLiteral(self, ctx:langParser.ObjectLiteralContext):
        pass


    # Enter a parse tree produced by langParser#literalPair.
    def enterLiteralPair(self, ctx:langParser.LiteralPairContext):
        pass

    # Exit a parse tree produced by langParser#literalPair.
    def exitLiteralPair(self, ctx:langParser.LiteralPairContext):
        pass


    # Enter a parse tree produced by langParser#newTuple.
    def enterNewTuple(self, ctx:langParser.NewTupleContext):
        pass

    # Exit a parse tree produced by langParser#newTuple.
    def exitNewTuple(self, ctx:langParser.NewTupleContext):
        pass


    # Enter a parse tree produced by langParser#negation.
    def enterNegation(self, ctx:langParser.NegationContext):
        pass

    # Exit a parse tree produced by langParser#negation.
    def exitNegation(self, ctx:langParser.NegationContext):
        pass


    # Enter a parse tree produced by langParser#string.
    def enterString(self, ctx:langParser.StringContext):
        pass

    # Exit a parse tree produced by langParser#string.
    def exitString(self, ctx:langParser.StringContext):
        pass


    # Enter a parse tree produced by langParser#toExitExpression.
    def enterToExitExpression(self, ctx:langParser.ToExitExpressionContext):
        pass

    # Exit a parse tree produced by langParser#toExitExpression.
    def exitToExitExpression(self, ctx:langParser.ToExitExpressionContext):
        pass


    # Enter a parse tree produced by langParser#lt.
    def enterLt(self, ctx:langParser.LtContext):
        pass

    # Exit a parse tree produced by langParser#lt.
    def exitLt(self, ctx:langParser.LtContext):
        pass


    # Enter a parse tree produced by langParser#toFunctionType.
    def enterToFunctionType(self, ctx:langParser.ToFunctionTypeContext):
        pass

    # Exit a parse tree produced by langParser#toFunctionType.
    def exitToFunctionType(self, ctx:langParser.ToFunctionTypeContext):
        pass


    # Enter a parse tree produced by langParser#subtraction.
    def enterSubtraction(self, ctx:langParser.SubtractionContext):
        pass

    # Exit a parse tree produced by langParser#subtraction.
    def exitSubtraction(self, ctx:langParser.SubtractionContext):
        pass


    # Enter a parse tree produced by langParser#toVoidType.
    def enterToVoidType(self, ctx:langParser.ToVoidTypeContext):
        pass

    # Exit a parse tree produced by langParser#toVoidType.
    def exitToVoidType(self, ctx:langParser.ToVoidTypeContext):
        pass


    # Enter a parse tree produced by langParser#toIf.
    def enterToIf(self, ctx:langParser.ToIfContext):
        pass

    # Exit a parse tree produced by langParser#toIf.
    def exitToIf(self, ctx:langParser.ToIfContext):
        pass


    # Enter a parse tree produced by langParser#toNewObject.
    def enterToNewObject(self, ctx:langParser.ToNewObjectContext):
        pass

    # Exit a parse tree produced by langParser#toNewObject.
    def exitToNewObject(self, ctx:langParser.ToNewObjectContext):
        pass


    # Enter a parse tree produced by langParser#division.
    def enterDivision(self, ctx:langParser.DivisionContext):
        pass

    # Exit a parse tree produced by langParser#division.
    def exitDivision(self, ctx:langParser.DivisionContext):
        pass


    # Enter a parse tree produced by langParser#boundDereference.
    def enterBoundDereference(self, ctx:langParser.BoundDereferenceContext):
        pass

    # Exit a parse tree produced by langParser#boundDereference.
    def exitBoundDereference(self, ctx:langParser.BoundDereferenceContext):
        pass


    # Enter a parse tree produced by langParser#number.
    def enterNumber(self, ctx:langParser.NumberContext):
        pass

    # Exit a parse tree produced by langParser#number.
    def exitNumber(self, ctx:langParser.NumberContext):
        pass


    # Enter a parse tree produced by langParser#toListType.
    def enterToListType(self, ctx:langParser.ToListTypeContext):
        pass

    # Exit a parse tree produced by langParser#toListType.
    def exitToListType(self, ctx:langParser.ToListTypeContext):
        pass


    # Enter a parse tree produced by langParser#toWhileLoop.
    def enterToWhileLoop(self, ctx:langParser.ToWhileLoopContext):
        pass

    # Exit a parse tree produced by langParser#toWhileLoop.
    def exitToWhileLoop(self, ctx:langParser.ToWhileLoopContext):
        pass


    # Enter a parse tree produced by langParser#toConstTypeModifier.
    def enterToConstTypeModifier(self, ctx:langParser.ToConstTypeModifierContext):
        pass

    # Exit a parse tree produced by langParser#toConstTypeModifier.
    def exitToConstTypeModifier(self, ctx:langParser.ToConstTypeModifierContext):
        pass


    # Enter a parse tree produced by langParser#toReturnExpression.
    def enterToReturnExpression(self, ctx:langParser.ToReturnExpressionContext):
        pass

    # Exit a parse tree produced by langParser#toReturnExpression.
    def exitToReturnExpression(self, ctx:langParser.ToReturnExpressionContext):
        pass


    # Enter a parse tree produced by langParser#gte.
    def enterGte(self, ctx:langParser.GteContext):
        pass

    # Exit a parse tree produced by langParser#gte.
    def exitGte(self, ctx:langParser.GteContext):
        pass


    # Enter a parse tree produced by langParser#multiplication.
    def enterMultiplication(self, ctx:langParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by langParser#multiplication.
    def exitMultiplication(self, ctx:langParser.MultiplicationContext):
        pass


    # Enter a parse tree produced by langParser#lte.
    def enterLte(self, ctx:langParser.LteContext):
        pass

    # Exit a parse tree produced by langParser#lte.
    def exitLte(self, ctx:langParser.LteContext):
        pass


    # Enter a parse tree produced by langParser#modulus.
    def enterModulus(self, ctx:langParser.ModulusContext):
        pass

    # Exit a parse tree produced by langParser#modulus.
    def exitModulus(self, ctx:langParser.ModulusContext):
        pass


    # Enter a parse tree produced by langParser#addition.
    def enterAddition(self, ctx:langParser.AdditionContext):
        pass

    # Exit a parse tree produced by langParser#addition.
    def exitAddition(self, ctx:langParser.AdditionContext):
        pass


    # Enter a parse tree produced by langParser#dynamicDereference.
    def enterDynamicDereference(self, ctx:langParser.DynamicDereferenceContext):
        pass

    # Exit a parse tree produced by langParser#dynamicDereference.
    def exitDynamicDereference(self, ctx:langParser.DynamicDereferenceContext):
        pass


    # Enter a parse tree produced by langParser#noParameterFunctionInvocation.
    def enterNoParameterFunctionInvocation(self, ctx:langParser.NoParameterFunctionInvocationContext):
        pass

    # Exit a parse tree produced by langParser#noParameterFunctionInvocation.
    def exitNoParameterFunctionInvocation(self, ctx:langParser.NoParameterFunctionInvocationContext):
        pass


    # Enter a parse tree produced by langParser#unboundDereference.
    def enterUnboundDereference(self, ctx:langParser.UnboundDereferenceContext):
        pass

    # Exit a parse tree produced by langParser#unboundDereference.
    def exitUnboundDereference(self, ctx:langParser.UnboundDereferenceContext):
        pass


    # Enter a parse tree produced by langParser#toObjectType.
    def enterToObjectType(self, ctx:langParser.ToObjectTypeContext):
        pass

    # Exit a parse tree produced by langParser#toObjectType.
    def exitToObjectType(self, ctx:langParser.ToObjectTypeContext):
        pass


    # Enter a parse tree produced by langParser#toDynamicFunctionLiteral.
    def enterToDynamicFunctionLiteral(self, ctx:langParser.ToDynamicFunctionLiteralContext):
        pass

    # Exit a parse tree produced by langParser#toDynamicFunctionLiteral.
    def exitToDynamicFunctionLiteral(self, ctx:langParser.ToDynamicFunctionLiteralContext):
        pass


    # Enter a parse tree produced by langParser#toFunctionLiteral.
    def enterToFunctionLiteral(self, ctx:langParser.ToFunctionLiteralContext):
        pass

    # Exit a parse tree produced by langParser#toFunctionLiteral.
    def exitToFunctionLiteral(self, ctx:langParser.ToFunctionLiteralContext):
        pass


    # Enter a parse tree produced by langParser#assignment.
    def enterAssignment(self, ctx:langParser.AssignmentContext):
        pass

    # Exit a parse tree produced by langParser#assignment.
    def exitAssignment(self, ctx:langParser.AssignmentContext):
        pass


    # Enter a parse tree produced by langParser#toNewTuple.
    def enterToNewTuple(self, ctx:langParser.ToNewTupleContext):
        pass

    # Exit a parse tree produced by langParser#toNewTuple.
    def exitToNewTuple(self, ctx:langParser.ToNewTupleContext):
        pass


    # Enter a parse tree produced by langParser#false.
    def enterFalse(self, ctx:langParser.FalseContext):
        pass

    # Exit a parse tree produced by langParser#false.
    def exitFalse(self, ctx:langParser.FalseContext):
        pass


    # Enter a parse tree produced by langParser#toAnyType.
    def enterToAnyType(self, ctx:langParser.ToAnyTypeContext):
        pass

    # Exit a parse tree produced by langParser#toAnyType.
    def exitToAnyType(self, ctx:langParser.ToAnyTypeContext):
        pass


    # Enter a parse tree produced by langParser#parenthesis.
    def enterParenthesis(self, ctx:langParser.ParenthesisContext):
        pass

    # Exit a parse tree produced by langParser#parenthesis.
    def exitParenthesis(self, ctx:langParser.ParenthesisContext):
        pass


    # Enter a parse tree produced by langParser#makePositive.
    def enterMakePositive(self, ctx:langParser.MakePositiveContext):
        pass

    # Exit a parse tree produced by langParser#makePositive.
    def exitMakePositive(self, ctx:langParser.MakePositiveContext):
        pass


    # Enter a parse tree produced by langParser#execute.
    def enterExecute(self, ctx:langParser.ExecuteContext):
        pass

    # Exit a parse tree produced by langParser#execute.
    def exitExecute(self, ctx:langParser.ExecuteContext):
        pass


    # Enter a parse tree produced by langParser#gt.
    def enterGt(self, ctx:langParser.GtContext):
        pass

    # Exit a parse tree produced by langParser#gt.
    def exitGt(self, ctx:langParser.GtContext):
        pass


    # Enter a parse tree produced by langParser#toStringType.
    def enterToStringType(self, ctx:langParser.ToStringTypeContext):
        pass

    # Exit a parse tree produced by langParser#toStringType.
    def exitToStringType(self, ctx:langParser.ToStringTypeContext):
        pass


    # Enter a parse tree produced by langParser#toIntegerType.
    def enterToIntegerType(self, ctx:langParser.ToIntegerTypeContext):
        pass

    # Exit a parse tree produced by langParser#toIntegerType.
    def exitToIntegerType(self, ctx:langParser.ToIntegerTypeContext):
        pass


    # Enter a parse tree produced by langParser#singleParameterFunctionInvocation.
    def enterSingleParameterFunctionInvocation(self, ctx:langParser.SingleParameterFunctionInvocationContext):
        pass

    # Exit a parse tree produced by langParser#singleParameterFunctionInvocation.
    def exitSingleParameterFunctionInvocation(self, ctx:langParser.SingleParameterFunctionInvocationContext):
        pass


    # Enter a parse tree produced by langParser#null.
    def enterNull(self, ctx:langParser.NullContext):
        pass

    # Exit a parse tree produced by langParser#null.
    def exitNull(self, ctx:langParser.NullContext):
        pass


    # Enter a parse tree produced by langParser#toTupleType.
    def enterToTupleType(self, ctx:langParser.ToTupleTypeContext):
        pass

    # Exit a parse tree produced by langParser#toTupleType.
    def exitToTupleType(self, ctx:langParser.ToTupleTypeContext):
        pass


    # Enter a parse tree produced by langParser#toInferredType.
    def enterToInferredType(self, ctx:langParser.ToInferredTypeContext):
        pass

    # Exit a parse tree produced by langParser#toInferredType.
    def exitToInferredType(self, ctx:langParser.ToInferredTypeContext):
        pass


    # Enter a parse tree produced by langParser#equals.
    def enterEquals(self, ctx:langParser.EqualsContext):
        pass

    # Exit a parse tree produced by langParser#equals.
    def exitEquals(self, ctx:langParser.EqualsContext):
        pass


    # Enter a parse tree produced by langParser#true.
    def enterTrue(self, ctx:langParser.TrueContext):
        pass

    # Exit a parse tree produced by langParser#true.
    def exitTrue(self, ctx:langParser.TrueContext):
        pass


    # Enter a parse tree produced by langParser#notEquals.
    def enterNotEquals(self, ctx:langParser.NotEqualsContext):
        pass

    # Exit a parse tree produced by langParser#notEquals.
    def exitNotEquals(self, ctx:langParser.NotEqualsContext):
        pass


    # Enter a parse tree produced by langParser#voidType.
    def enterVoidType(self, ctx:langParser.VoidTypeContext):
        pass

    # Exit a parse tree produced by langParser#voidType.
    def exitVoidType(self, ctx:langParser.VoidTypeContext):
        pass


    # Enter a parse tree produced by langParser#inferredType.
    def enterInferredType(self, ctx:langParser.InferredTypeContext):
        pass

    # Exit a parse tree produced by langParser#inferredType.
    def exitInferredType(self, ctx:langParser.InferredTypeContext):
        pass


    # Enter a parse tree produced by langParser#integerType.
    def enterIntegerType(self, ctx:langParser.IntegerTypeContext):
        pass

    # Exit a parse tree produced by langParser#integerType.
    def exitIntegerType(self, ctx:langParser.IntegerTypeContext):
        pass


    # Enter a parse tree produced by langParser#stringType.
    def enterStringType(self, ctx:langParser.StringTypeContext):
        pass

    # Exit a parse tree produced by langParser#stringType.
    def exitStringType(self, ctx:langParser.StringTypeContext):
        pass


    # Enter a parse tree produced by langParser#functionType.
    def enterFunctionType(self, ctx:langParser.FunctionTypeContext):
        pass

    # Exit a parse tree produced by langParser#functionType.
    def exitFunctionType(self, ctx:langParser.FunctionTypeContext):
        pass


    # Enter a parse tree produced by langParser#objectType.
    def enterObjectType(self, ctx:langParser.ObjectTypeContext):
        pass

    # Exit a parse tree produced by langParser#objectType.
    def exitObjectType(self, ctx:langParser.ObjectTypeContext):
        pass


    # Enter a parse tree produced by langParser#listType.
    def enterListType(self, ctx:langParser.ListTypeContext):
        pass

    # Exit a parse tree produced by langParser#listType.
    def exitListType(self, ctx:langParser.ListTypeContext):
        pass


    # Enter a parse tree produced by langParser#tupleType.
    def enterTupleType(self, ctx:langParser.TupleTypeContext):
        pass

    # Exit a parse tree produced by langParser#tupleType.
    def exitTupleType(self, ctx:langParser.TupleTypeContext):
        pass


    # Enter a parse tree produced by langParser#anyType.
    def enterAnyType(self, ctx:langParser.AnyTypeContext):
        pass

    # Exit a parse tree produced by langParser#anyType.
    def exitAnyType(self, ctx:langParser.AnyTypeContext):
        pass


    # Enter a parse tree produced by langParser#constTypeModifier.
    def enterConstTypeModifier(self, ctx:langParser.ConstTypeModifierContext):
        pass

    # Exit a parse tree produced by langParser#constTypeModifier.
    def exitConstTypeModifier(self, ctx:langParser.ConstTypeModifierContext):
        pass


    # Enter a parse tree produced by langParser#propertyType.
    def enterPropertyType(self, ctx:langParser.PropertyTypeContext):
        pass

    # Exit a parse tree produced by langParser#propertyType.
    def exitPropertyType(self, ctx:langParser.PropertyTypeContext):
        pass


    # Enter a parse tree produced by langParser#whileLoop.
    def enterWhileLoop(self, ctx:langParser.WhileLoopContext):
        pass

    # Exit a parse tree produced by langParser#whileLoop.
    def exitWhileLoop(self, ctx:langParser.WhileLoopContext):
        pass


    # Enter a parse tree produced by langParser#ifBlock.
    def enterIfBlock(self, ctx:langParser.IfBlockContext):
        pass

    # Exit a parse tree produced by langParser#ifBlock.
    def exitIfBlock(self, ctx:langParser.IfBlockContext):
        pass


    # Enter a parse tree produced by langParser#functionLiteral.
    def enterFunctionLiteral(self, ctx:langParser.FunctionLiteralContext):
        pass

    # Exit a parse tree produced by langParser#functionLiteral.
    def exitFunctionLiteral(self, ctx:langParser.FunctionLiteralContext):
        pass


    # Enter a parse tree produced by langParser#functionArgumentAndReturns.
    def enterFunctionArgumentAndReturns(self, ctx:langParser.FunctionArgumentAndReturnsContext):
        pass

    # Exit a parse tree produced by langParser#functionArgumentAndReturns.
    def exitFunctionArgumentAndReturns(self, ctx:langParser.FunctionArgumentAndReturnsContext):
        pass


    # Enter a parse tree produced by langParser#functionThrows.
    def enterFunctionThrows(self, ctx:langParser.FunctionThrowsContext):
        pass

    # Exit a parse tree produced by langParser#functionThrows.
    def exitFunctionThrows(self, ctx:langParser.FunctionThrowsContext):
        pass


    # Enter a parse tree produced by langParser#functionExits.
    def enterFunctionExits(self, ctx:langParser.FunctionExitsContext):
        pass

    # Exit a parse tree produced by langParser#functionExits.
    def exitFunctionExits(self, ctx:langParser.FunctionExitsContext):
        pass


    # Enter a parse tree produced by langParser#returnExpression.
    def enterReturnExpression(self, ctx:langParser.ReturnExpressionContext):
        pass

    # Exit a parse tree produced by langParser#returnExpression.
    def exitReturnExpression(self, ctx:langParser.ReturnExpressionContext):
        pass


    # Enter a parse tree produced by langParser#exitExpression.
    def enterExitExpression(self, ctx:langParser.ExitExpressionContext):
        pass

    # Exit a parse tree produced by langParser#exitExpression.
    def exitExitExpression(self, ctx:langParser.ExitExpressionContext):
        pass


