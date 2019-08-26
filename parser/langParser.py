# Generated from lang.g4 by ANTLR 4.7.2
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\26c\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\4\b\t\b\4\t\t\t\4\n\t\n\3\2\3\2\3\3\3\3\3\3\3\3\7\3")
        buf.write(u"\33\n\3\f\3\16\3\36\13\3\3\3\3\3\3\3\3\3\5\3$\n\3\3\4")
        buf.write(u"\3\4\3\4\3\4\3\5\3\5\3\5\3\5\7\5.\n\5\f\5\16\5\61\13")
        buf.write(u"\5\3\5\3\5\3\5\3\5\5\5\67\n\5\3\6\3\6\3\6\3\6\3\6\3\6")
        buf.write(u"\3\6\3\6\3\6\3\6\3\6\5\6D\n\6\3\7\3\7\3\7\3\7\3\7\3\7")
        buf.write(u"\3\7\7\7M\n\7\f\7\16\7P\13\7\3\7\3\7\3\b\3\b\3\b\3\t")
        buf.write(u"\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n\3\n\5\na\n\n\3\n\2\2")
        buf.write(u"\13\2\4\6\b\n\f\16\20\22\2\2\2i\2\24\3\2\2\2\4#\3\2\2")
        buf.write(u"\2\6%\3\2\2\2\b\66\3\2\2\2\nC\3\2\2\2\fE\3\2\2\2\16S")
        buf.write(u"\3\2\2\2\20V\3\2\2\2\22Z\3\2\2\2\24\25\5\n\6\2\25\3\3")
        buf.write(u"\2\2\2\26\27\7\3\2\2\27\34\5\6\4\2\30\31\7\4\2\2\31\33")
        buf.write(u"\5\6\4\2\32\30\3\2\2\2\33\36\3\2\2\2\34\32\3\2\2\2\34")
        buf.write(u"\35\3\2\2\2\35\37\3\2\2\2\36\34\3\2\2\2\37 \7\5\2\2 ")
        buf.write(u"$\3\2\2\2!\"\7\3\2\2\"$\7\5\2\2#\26\3\2\2\2#!\3\2\2\2")
        buf.write(u"$\5\3\2\2\2%&\7\24\2\2&\'\7\6\2\2\'(\5\n\6\2(\7\3\2\2")
        buf.write(u"\2)*\7\7\2\2*/\5\n\6\2+,\7\4\2\2,.\5\n\6\2-+\3\2\2\2")
        buf.write(u".\61\3\2\2\2/-\3\2\2\2/\60\3\2\2\2\60\62\3\2\2\2\61/")
        buf.write(u"\3\2\2\2\62\63\7\b\2\2\63\67\3\2\2\2\64\65\7\7\2\2\65")
        buf.write(u"\67\7\b\2\2\66)\3\2\2\2\66\64\3\2\2\2\67\t\3\2\2\28D")
        buf.write(u"\7\24\2\29D\7\25\2\2:D\5\4\3\2;D\5\b\5\2<D\7\t\2\2=D")
        buf.write(u"\7\n\2\2>D\7\13\2\2?D\5\f\7\2@D\5\16\b\2AD\5\20\t\2B")
        buf.write(u"D\5\22\n\2C8\3\2\2\2C9\3\2\2\2C:\3\2\2\2C;\3\2\2\2C<")
        buf.write(u"\3\2\2\2C=\3\2\2\2C>\3\2\2\2C?\3\2\2\2C@\3\2\2\2CA\3")
        buf.write(u"\2\2\2CB\3\2\2\2D\13\3\2\2\2EF\7\f\2\2FG\7\r\2\2GH\7")
        buf.write(u"\16\2\2HN\7\3\2\2IJ\5\n\6\2JK\7\17\2\2KM\3\2\2\2LI\3")
        buf.write(u"\2\2\2MP\3\2\2\2NL\3\2\2\2NO\3\2\2\2OQ\3\2\2\2PN\3\2")
        buf.write(u"\2\2QR\7\5\2\2R\r\3\2\2\2ST\7\20\2\2TU\5\4\3\2U\17\3")
        buf.write(u"\2\2\2VW\5\22\n\2WX\7\21\2\2XY\5\n\6\2Y\21\3\2\2\2Z`")
        buf.write(u"\7\23\2\2[a\3\2\2\2\\]\5\n\6\2]^\7\22\2\2^_\7\23\2\2")
        buf.write(u"_a\3\2\2\2`[\3\2\2\2`\\\3\2\2\2a\23\3\2\2\2\t\34#/\66")
        buf.write(u"CN`")
        return buf.getvalue()


class langParser ( Parser ):

    grammarFileName = "lang.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'{'", u"','", u"'}'", u"':'", u"'['", 
                     u"']'", u"'true'", u"'false'", u"'null'", u"'function'", 
                     u"'('", u"')'", u"';'", u"'method'", u"'='", u"'.'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"SYMBOL", u"STRING", u"NUMBER", u"WS" ]

    RULE_code = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_array = 3
    RULE_expression = 4
    RULE_functionInstantiation = 5
    RULE_methodInstantiation = 6
    RULE_assignment = 7
    RULE_dereference = 8

    ruleNames =  [ u"code", u"obj", u"pair", u"array", u"expression", u"functionInstantiation", 
                   u"methodInstantiation", u"assignment", u"dereference" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    SYMBOL=17
    STRING=18
    NUMBER=19
    WS=20

    def __init__(self, input, output=sys.stdout):
        super(langParser, self).__init__(input, output=output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class CodeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.CodeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(langParser.ExpressionContext,0)


        def getRuleIndex(self):
            return langParser.RULE_code

        def enterRule(self, listener):
            if hasattr(listener, "enterCode"):
                listener.enterCode(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCode"):
                listener.exitCode(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCode"):
                return visitor.visitCode(self)
            else:
                return visitor.visitChildren(self)




    def code(self):

        localctx = langParser.CodeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_code)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ObjContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.ObjContext, self).__init__(parent, invokingState)
            self.parser = parser

        def pair(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(langParser.PairContext)
            else:
                return self.getTypedRuleContext(langParser.PairContext,i)


        def getRuleIndex(self):
            return langParser.RULE_obj

        def enterRule(self, listener):
            if hasattr(listener, "enterObj"):
                listener.enterObj(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitObj"):
                listener.exitObj(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitObj"):
                return visitor.visitObj(self)
            else:
                return visitor.visitChildren(self)




    def obj(self):

        localctx = langParser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 33
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 20
                self.match(langParser.T__0)
                self.state = 21
                self.pair()
                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==langParser.T__1:
                    self.state = 22
                    self.match(langParser.T__1)
                    self.state = 23
                    self.pair()
                    self.state = 28
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 29
                self.match(langParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 31
                self.match(langParser.T__0)
                self.state = 32
                self.match(langParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PairContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.PairContext, self).__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(langParser.STRING, 0)

        def expression(self):
            return self.getTypedRuleContext(langParser.ExpressionContext,0)


        def getRuleIndex(self):
            return langParser.RULE_pair

        def enterRule(self, listener):
            if hasattr(listener, "enterPair"):
                listener.enterPair(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPair"):
                listener.exitPair(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPair"):
                return visitor.visitPair(self)
            else:
                return visitor.visitChildren(self)




    def pair(self):

        localctx = langParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self.match(langParser.STRING)
            self.state = 36
            self.match(langParser.T__3)
            self.state = 37
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.ArrayContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(langParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(langParser.ExpressionContext,i)


        def getRuleIndex(self):
            return langParser.RULE_array

        def enterRule(self, listener):
            if hasattr(listener, "enterArray"):
                listener.enterArray(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitArray"):
                listener.exitArray(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitArray"):
                return visitor.visitArray(self)
            else:
                return visitor.visitChildren(self)




    def array(self):

        localctx = langParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 52
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 39
                self.match(langParser.T__4)
                self.state = 40
                self.expression()
                self.state = 45
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==langParser.T__1:
                    self.state = 41
                    self.match(langParser.T__1)
                    self.state = 42
                    self.expression()
                    self.state = 47
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 48
                self.match(langParser.T__5)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 50
                self.match(langParser.T__4)
                self.state = 51
                self.match(langParser.T__5)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.ExpressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(langParser.STRING, 0)

        def NUMBER(self):
            return self.getToken(langParser.NUMBER, 0)

        def obj(self):
            return self.getTypedRuleContext(langParser.ObjContext,0)


        def array(self):
            return self.getTypedRuleContext(langParser.ArrayContext,0)


        def functionInstantiation(self):
            return self.getTypedRuleContext(langParser.FunctionInstantiationContext,0)


        def methodInstantiation(self):
            return self.getTypedRuleContext(langParser.MethodInstantiationContext,0)


        def assignment(self):
            return self.getTypedRuleContext(langParser.AssignmentContext,0)


        def dereference(self):
            return self.getTypedRuleContext(langParser.DereferenceContext,0)


        def getRuleIndex(self):
            return langParser.RULE_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterExpression"):
                listener.enterExpression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExpression"):
                listener.exitExpression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitExpression"):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = langParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_expression)
        try:
            self.state = 65
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 54
                self.match(langParser.STRING)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 55
                self.match(langParser.NUMBER)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 56
                self.obj()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 57
                self.array()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 58
                self.match(langParser.T__6)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 59
                self.match(langParser.T__7)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 60
                self.match(langParser.T__8)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 61
                self.functionInstantiation()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 62
                self.methodInstantiation()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 63
                self.assignment()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 64
                self.dereference()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionInstantiationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.FunctionInstantiationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(langParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(langParser.ExpressionContext,i)


        def getRuleIndex(self):
            return langParser.RULE_functionInstantiation

        def enterRule(self, listener):
            if hasattr(listener, "enterFunctionInstantiation"):
                listener.enterFunctionInstantiation(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFunctionInstantiation"):
                listener.exitFunctionInstantiation(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitFunctionInstantiation"):
                return visitor.visitFunctionInstantiation(self)
            else:
                return visitor.visitChildren(self)




    def functionInstantiation(self):

        localctx = langParser.FunctionInstantiationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_functionInstantiation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(langParser.T__9)
            self.state = 68
            self.match(langParser.T__10)
            self.state = 69
            self.match(langParser.T__11)
            self.state = 70
            self.match(langParser.T__0)
            self.state = 76
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << langParser.T__0) | (1 << langParser.T__4) | (1 << langParser.T__6) | (1 << langParser.T__7) | (1 << langParser.T__8) | (1 << langParser.T__9) | (1 << langParser.T__13) | (1 << langParser.SYMBOL) | (1 << langParser.STRING) | (1 << langParser.NUMBER))) != 0):
                self.state = 71
                self.expression()
                self.state = 72
                self.match(langParser.T__12)
                self.state = 78
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 79
            self.match(langParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MethodInstantiationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.MethodInstantiationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def obj(self):
            return self.getTypedRuleContext(langParser.ObjContext,0)


        def getRuleIndex(self):
            return langParser.RULE_methodInstantiation

        def enterRule(self, listener):
            if hasattr(listener, "enterMethodInstantiation"):
                listener.enterMethodInstantiation(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMethodInstantiation"):
                listener.exitMethodInstantiation(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMethodInstantiation"):
                return visitor.visitMethodInstantiation(self)
            else:
                return visitor.visitChildren(self)




    def methodInstantiation(self):

        localctx = langParser.MethodInstantiationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_methodInstantiation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.match(langParser.T__13)
            self.state = 82
            self.obj()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.AssignmentContext, self).__init__(parent, invokingState)
            self.parser = parser

        def dereference(self):
            return self.getTypedRuleContext(langParser.DereferenceContext,0)


        def expression(self):
            return self.getTypedRuleContext(langParser.ExpressionContext,0)


        def getRuleIndex(self):
            return langParser.RULE_assignment

        def enterRule(self, listener):
            if hasattr(listener, "enterAssignment"):
                listener.enterAssignment(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAssignment"):
                listener.exitAssignment(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitAssignment"):
                return visitor.visitAssignment(self)
            else:
                return visitor.visitChildren(self)




    def assignment(self):

        localctx = langParser.AssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 84
            self.dereference()
            self.state = 85
            self.match(langParser.T__14)
            self.state = 86
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DereferenceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(langParser.DereferenceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SYMBOL(self, i=None):
            if i is None:
                return self.getTokens(langParser.SYMBOL)
            else:
                return self.getToken(langParser.SYMBOL, i)

        def expression(self):
            return self.getTypedRuleContext(langParser.ExpressionContext,0)


        def getRuleIndex(self):
            return langParser.RULE_dereference

        def enterRule(self, listener):
            if hasattr(listener, "enterDereference"):
                listener.enterDereference(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDereference"):
                listener.exitDereference(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitDereference"):
                return visitor.visitDereference(self)
            else:
                return visitor.visitChildren(self)




    def dereference(self):

        localctx = langParser.DereferenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_dereference)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 88
            self.match(langParser.SYMBOL)
            self.state = 94
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [langParser.EOF, langParser.T__1, langParser.T__2, langParser.T__5, langParser.T__12, langParser.T__14, langParser.T__15]:
                pass
            elif token in [langParser.T__0, langParser.T__4, langParser.T__6, langParser.T__7, langParser.T__8, langParser.T__9, langParser.T__13, langParser.SYMBOL, langParser.STRING, langParser.NUMBER]:
                self.state = 90
                self.expression()
                self.state = 91
                self.match(langParser.T__15)
                self.state = 92
                self.match(langParser.SYMBOL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





