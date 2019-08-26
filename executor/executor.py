from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from parser.langLexer import langLexer
from parser.langListener import langListener
from parser.langParser import langParser
from parser.langVisitor import langVisitor


class BreakException(Exception):
    def __init__(self, type, value):
        self.type = type
        self.value = value

OPCODES = {
}

def enrich_opcode(data):
    return OPCODES.get(data["opcode"])(data)

def evaluate(expression):
    try:
        expression.jump()
    except BreakException as e:
        if e.type == "value":
            return e.value
        else:
            raise

class FunctionExecutor(object):
    def __init__(self, data):
        self.data = data

        static_code = enrich_opcode(self.data["statics"])
        self.statics = evaluate(static_code)
        self.code = enrich_opcode(self.data["code"])

        break_types = self.code.get_break_types()
        # Check break_types lines up with self.statics

    def execute(self):
        evaluate(self.code)

def execute(ast):
    executor = FunctionExecutor(ast)
    executor.execute()
