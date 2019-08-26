# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from unittest.case import TestCase
import unittest.main

from parser.parser import parse


class TestJSONParsing(TestCase):
    maxDiff = 65536

    def test_number(self):
        ast = parse("""
            42
        """)
        self.assertEquals(ast, 42)

    def test_string(self):
        ast = parse("""
            "hello world"
        """)
        self.assertEquals(ast, "hello world")

    def test_empty_object(self):
        ast = parse("""
            {}
        """)
        self.assertEquals(ast, { })        

    def test_object(self):
        ast = parse("""
            { "foo": "bar" }
        """)
        self.assertEquals(ast, { "foo": "bar" })

    def test_nested_object(self):
        ast = parse("""
            { "foo": {
                "bar": 42
            } }
        """)
        self.assertEquals(ast, { "foo": { "bar": 42 } })

class TestFunctionParsing(TestCase):
    maxDiff = 65536

    def test_empty_function(self):
        ast = parse("""
            function () { }
        """)
        self.assertEquals(ast, {
            "statics": {
                "opcode": "literal",
                "value": {}
            },
            "code": {
                "opcode": "comma",
                "expressions": []
            }
        })

    def test_simple_assignment_function(self):
        ast = parse("""
            function() { local = 42; }
        """)
        self.assertEquals(ast, {
            "statics": {
                "opcode": "literal",
                "value": {}
            },
            "code": {
                "opcode": "comma",
                "expressions": [{
                    "opcode": "assignment",
                    "lvalue": {
                        "opcode": "dereference",
                        "reference": {
                            "opcode": "literal",
                            "value": "local"
                        },
                        "of": {
                            "opcode": "dereference",
                            "reference": {
                                "opcode": "literal",
                                "value": "compound"
                            },
                        }
                    },
                    "rvalue": {
                        "opcode": "literal",
                        "value": 42.0
                    }
                }]
            }
        })

    def test_simple_return_function(self):
        ast = parse("""
            function() { return 42; }
        """)
        self.assertEquals(ast, {
            "statics": {
                "opcode": "literal",
                "value": {}
            },
            "code": {
                "opcode": "comma",
                "expressions": [{
                    "opcode": "break",
                    "type": "return",
                    "value": {
                        "opcode": "literal",
                        "value": 42
                    }
                }]
            }
        })

class TestStaticEvaluation(TestCase):
    def test_static_evaluation(self):
        ast = parse("""
            method {
                "statics": {
                    "opcode": "literal",
                    "value": 42
                },
                "code": {}
            }
        """)

        self.assertEquals(ast, {
            "statics": {
                "opcode": "literal",
                "value": 42
            },
            "code": {}
        })
