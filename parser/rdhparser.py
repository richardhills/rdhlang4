# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ErrorListener, ConsoleErrorListener

from parser.langLexer import langLexer
from parser.langParser import langParser
from parser.visitor import RDHLang4Visitor, ParseError


class AlwaysFailErrorListener(ConsoleErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        super(AlwaysFailErrorListener, self).syntaxError(recognizer, offendingSymbol, line, column, msg, e)
        raise ParseError()

def parse(code, debug=False):
    print "Parsing {}".format(code)
    lexer = langLexer(InputStream(code))
    tokens = CommonTokenStream(lexer)
    parser = langParser(tokens)
    parser.addErrorListener(AlwaysFailErrorListener())
    ast = parser.code()
    visitor = RDHLang4Visitor(debug=debug)
    return visitor.visit(ast)
