# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from _hashlib import new
import json
import unittest
from unittest.case import TestCase

from parser.rdhparser import parse
from parser.visitor import comma_op, literal_op, break_op, addition_op, \
    object_type, function_type, prepare_op, new_object_op, \
    assignment_op, symbolic_dereference_ops, type, merge_op, function_literal, \
    catch_op, jump_op, nop, symbolic_dereference_ops, dereference_op
from type_system.core_types import IntegerType
from imaplib import Literal


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
        CORRECT = { "foo": "bar" }
        self.assertEquals(ast, CORRECT)

    def test_nested_object(self):
        ast = parse("""
            { "foo": {
                "bar": 42
            } }
        """)
        CORRECT = { "foo": { "bar": 42 } }
        self.assertEquals(ast, CORRECT)


class TestFunctionParsing(TestCase):
    maxDiff = 65536

    def test_empty_function(self):
        ast = parse("""
            function () nothrow { }
        """)
        self.assertEquals(
            ast,
            {
                "static": new_object_op({
                    "breaks": new_object_op({
                        "return": type("Void")
                    }),
                    "local": object_type({}),
                    "argument": type("Void"),
                }),
                "local_initializer": new_object_op({}),
            }
        )

    def test_simple_assignment_function(self):
        ast = parse("""
            function() nothrow { local = 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({}),
                "argument": type("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": assignment_op(
                symbolic_dereference_ops(["local"]),
                literal_op(42)
            )
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

    def test_simple_return_function(self):
        ast = parse("""
            function() nothrow { return 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({}),
                "argument": type("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": break_op("return", literal_op(42))
        }

        print json.dumps(ast)
        print json.dumps(CORRECT)

        self.assertEquals(ast, CORRECT)

    def test_simple_return_function_with_types(self):
        ast = parse("""
            function(String => Integer) nothrow { return 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Integer")
                }),
                "local": object_type({}),
                "argument": type("String")
            }),
            "local_initializer": new_object_op({}),
            "code": break_op("return", literal_op(42))
        }

        self.assertEquals(ast, CORRECT)

    def test_addition(self):
        ast = parse("""
            function() nothrow { 4 + 38; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({}),
                "argument": type("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": addition_op(literal_op(4), literal_op(38))
        }

        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)


class TestLocalVariables(TestCase):
    def test_basic_variable(self):
        ast = parse("""
            function(Void => Void) nothrow {
                Integer foo = 42;
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type("Void"),
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({
                    "foo": type("Integer")
                }),
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            })
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

    def test_return_basic_variable(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                Integer foo = 42;
                return foo;
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type("Void"),
                "breaks": new_object_op({
                    "return": type("Integer")
                }),
                "local": object_type({
                    "foo": type("Integer")
                }),
            }),
            "code": break_op("return", symbolic_dereference_ops(["foo"])),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            })
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

    def test_2_local_variables(self):
        ast = parse("""
            function(Void => Void) nothrow {
                Integer foo = 42;
                String bar = "hello";
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type("Void"),
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({
                    "foo": type("Integer")
                })
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            }),
            "code": jump_op(prepare_op(literal_op({
                "static": new_object_op({
                    "argument": type("Void"),
                    "breaks": new_object_op({
                        "return": type("Void")
                    }),
                    "local": object_type({
                        "foo": type("Integer"),
                        "bar": type("String")
                    }),
                }),
                "local_initializer": merge_op(
                    symbolic_dereference_ops(["outer", "local"]),
                    new_object_op({
                        "bar": literal_op("hello")
                    })
                )
            })), nop())
        }

        print json.dumps(ast)
        print json.dumps(CORRECT)

        self.assertEquals(ast, CORRECT)


    def test_2_local_variables_with_mutation(self):
        ast = parse("""
            function(Void => Void) nothrow {
                Integer foo = 42;
                foo = foo + 3;
                String bar = "hello";
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type("Void"),
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({
                    "foo": type("Integer")
                })
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            }),
            "code": comma_op([
                assignment_op(
                    symbolic_dereference_ops(["foo"]),
                    addition_op(symbolic_dereference_ops(["foo"]), literal_op(3))
                ),
                jump_op(prepare_op(literal_op({
                    "static": new_object_op({
                        "argument": type("Void"),
                        "breaks": new_object_op({
                            "return": type("Void")
                        }),
                        "local": object_type({
                            "foo": type("Integer"),
                            "bar": type("String")
                        })
                    }),
                    "local_initializer": merge_op(
                        symbolic_dereference_ops(["outer", "local"]),
                        new_object_op({
                            "bar": literal_op("hello")
                        })
                    )
                })), nop())
            ])
        }

        print json.dumps(ast)
        print json.dumps(CORRECT)

        self.assertEquals(ast, CORRECT)

class TestObjectTypes(TestCase):
    def test_basic_object(self):
        ast = parse("""
            function(Void => Void) nothrow {
                Object {
                    Integer bar;
                } foo = { bar: 5 };
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Void")
                }),
                "local": object_type({
                    "foo": object_type({
                        "bar": type("Integer")
                    })
                }),
                "argument": type("Void")
            }),
            "local_initializer": new_object_op({
                "foo": new_object_op({ "bar": literal_op(5) })
            })
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

class TestNestedFunctions(TestCase):

    def test_nested_function(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                Function<Void => Integer> foo = function(Void => Integer) nothrow {
                    return 42;
                };
                return foo();
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type("Integer")
                }),
                "local": object_type({
                    "foo": function_type(
                        type("Void"), {
                            "return": type("Integer")
                        }
                    )
                }),
                "argument": type("Void")
            }),
            "local_initializer": new_object_op({
                "foo": prepare_op(literal_op(function_literal(
                    type("Void"), new_object_op({ "return": type("Integer") }), object_type({}), new_object_op({}), [
                        break_op("return", literal_op(42))
                    ]
                )))
            }),
            "code":
                break_op("return",
                    catch_op("return", jump_op(symbolic_dereference_ops(["foo"]), nop()))
                )
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)



if __name__ == '__main__':
    unittest.main()

