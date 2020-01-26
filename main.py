from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from parser.langLexer import langLexer
from parser.langParser import langParser
from rdhlang4.executor.test import TestMiscelaneous

TestMiscelaneous

def main():
    code = """{
        "static": {
            "opcode": "literal",
            "value": 42
        },
        "code": {
            "opcode": "literal",
            "value": 5
        }
    }"""
    lexer = langLexer(InputStream(code))
    tokens  = CommonTokenStream(lexer)
    parser = langParser(tokens)
    ast = parser.code()
    print ast

if __name__ == "__main__":
    main()
