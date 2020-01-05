# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ConsoleErrorListener

from rdhlang4.executor.executor import PreparedFunction, \
    enforce_application_break_mode_constraints
from rdhlang4.parser.langLexer import langLexer
from rdhlang4.parser.langParser import langParser
from rdhlang4.parser.visitor import RDHLang4Visitor, ParseError
from rdhlang4.type_system.values import Object
from rdhlang4.utils import NO_VALUE


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

def prepare_code(code, debug=False, check_application_break_mode_constraints=True, include_stdlib=True):
    ast = parse(code, debug)

    if ast and isinstance(ast, dict) and "static" in ast:
        if include_stdlib:
            from rdhlang4.executor.stdlib import add_function
            top_context = Object({
                "static": Object({
                    "add": add_function
                })
            })
        else:
            top_context = NO_VALUE
        function = PreparedFunction(ast, top_context)
        if check_application_break_mode_constraints:
            enforce_application_break_mode_constraints(function)
        return function
    return ast
