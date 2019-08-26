# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from parser.langLexer import langLexer
from parser.langListener import langListener
from parser.langParser import langParser
from parser.langVisitor import langVisitor
from parser.visitor import RDHLang4Visitor


def parse(code):
    print "Parsing {}".format(code)
    lexer = langLexer(InputStream(code))
    tokens  = CommonTokenStream(lexer)
    parser = langParser(tokens)
    ast = parser.code()
    visitor = RDHLang4Visitor()
    return visitor.visit(ast)
