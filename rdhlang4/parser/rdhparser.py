# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ConsoleErrorListener

from rdhlang4.executor.executor import PreparedFunction
from rdhlang4.parser.langLexer import langLexer
from rdhlang4.parser.langParser import langParser
from rdhlang4.parser.visitor import RDHLang4Visitor, ParseError


class AlwaysFailErrorListener(ConsoleErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        super(AlwaysFailErrorListener, self).syntaxError(recognizer, offendingSymbol, line, column, msg, e)
        raise ParseError()

#     def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
#         super(AlwaysFailErrorListener, self).reportAmbiguity(recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs)
#         raise ParseError()

def parse(code, debug=False):
    lexer = langLexer(InputStream(code))
    lexer.addErrorListener(AlwaysFailErrorListener())
    tokens = CommonTokenStream(lexer)
    parser = langParser(tokens)
    parser.addErrorListener(AlwaysFailErrorListener())
    ast = parser.code()
    visitor = RDHLang4Visitor(debug=debug)
    return visitor.visit(ast)

def prepare_code(code, debug=False):
    ast = parse(code, debug)

    if ast and isinstance(ast, dict) and "static" in ast:
        return PreparedFunction(ast)
    return ast
