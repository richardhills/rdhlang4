# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
from unittest.case import TestCase

from rdhlang4.parser.rdhparser import parse
from rdhlang4.parser.visitor import new_object_op, type_op, object_type, assignment_op, \
    symbolic_dereference_ops, literal_op, break_op, jump_op, \
    prepare_op, nop, comma_op, transform_op, function_type, catch_op, \
    binary_op


class TestJSONParsing(TestCase):
    maxDiff = 65536

    def test_number(self):
        ast = parse("""
            42
        """)
        self.assertEqual(ast, 42)

    def test_string(self):
        ast = parse("""
            "hello world"
        """)
        self.assertEqual(ast, "hello world")

    def test_empty_object(self):
        ast = parse("""
            {}
        """)
        self.assertEqual(ast, { })        

    def test_object(self):
        ast = parse("""
            { "foo": "bar" }
        """)
        CORRECT = { "foo": "bar" }
        self.assertEqual(ast, CORRECT)

    def test_nested_object(self):
        ast = parse("""
            { "foo": {
                "bar": 42
            } }
        """)
        CORRECT = { "foo": { "bar": 42 } }
        self.assertEqual(ast, CORRECT)


class TestFunctionParsing(TestCase):
    maxDiff = 65536

    def test_empty_function(self):
        ast = parse("""
            function () nothrow noexit { }
        """)
        self.assertEqual(
            ast,
            {
                "static": new_object_op({
                    "breaks": new_object_op({
                        "return": type_op("Inferred")
                    }),
                    "local": object_type({}),
                    "argument": type_op("Void"),
                }),
                "local_initializer": new_object_op({}),
                "code": break_op("return", nop())
            }
        )

    def test_simple_assignment_function(self):
        ast = parse("""
            function() nothrow noexit { local = 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Inferred")
                }),
                "local": object_type({}),
                "argument": type_op("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": assignment_op(
                symbolic_dereference_ops(["local"]),
                literal_op(42)
            )
        }
        self.assertEqual(ast, CORRECT)

    def test_simple_return_function(self):
        ast = parse("""
            function() nothrow noexit { return 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Inferred")
                }),
                "local": object_type({}),
                "argument": type_op("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": break_op("return", literal_op(42))
        }

        self.assertEqual(ast, CORRECT)

    def test_simple_return_function_with_types(self):
        ast = parse("""
            function(String => Integer) nothrow noexit { return 42; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Integer")
                }),
                "local": object_type({}),
                "argument": type_op("String")
            }),
            "local_initializer": new_object_op({}),
            "code": break_op("return", literal_op(42))
        }

        self.assertEqual(ast, CORRECT)

    def test_addition(self):
        ast = parse("""
            function() nothrow noexit { 4 + 38; }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Inferred")
                }),
                "local": object_type({}),
                "argument": type_op("Void")
            }),
            "local_initializer": new_object_op({}),
            "code": binary_op("addition", literal_op(4), literal_op(38))
        }

        self.assertEqual(ast, CORRECT)


class TestLocalVariables(TestCase):
    def test_basic_variable(self):
        ast = parse("""
            function(Void => Void) nothrow noexit {
                Integer foo = 42;
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type_op("Void"),
                "breaks": new_object_op({
                    "return": type_op("Void")
                }),
                "local": object_type({
                    "foo": type_op("Integer")
                }),
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            }),
            "code": break_op("return", nop())
        }
        self.assertEqual(ast, CORRECT)

    def test_return_basic_variable(self):
        ast = parse("""
            function(Void => Integer) nothrow noexit {
                Integer foo = 42;
                return foo;
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type_op("Void"),
                "breaks": new_object_op({
                    "return": type_op("Integer")
                }),
                "local": object_type({
                    "foo": type_op("Integer")
                }),
            }),
            "code": break_op("return", symbolic_dereference_ops(["foo"])),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            })
        }
        self.assertEqual(ast, CORRECT)

    def test_2_local_variables(self):
        ast = parse("""
            function(Void => Void) nothrow noexit {
                Integer foo = 42;
                String bar = "hello";
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type_op("Void"),
                "breaks": new_object_op({
                    "return": type_op("Void")
                }),
                "local": object_type({
                    "foo": type_op("Integer")
                })
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            }),
            "code": catch_op("function_stub_finished", jump_op(prepare_op(literal_op({
                "static": new_object_op({
                    "argument": type_op("Void"),
                    "breaks": new_object_op({
                        "all": type_op("Inferred")
                    }),
                    "local": object_type({
                        "bar": type_op("String")
                    }),
                }),
                "local_initializer": new_object_op({
                    "bar": literal_op("hello")
                }),
                "code": break_op("function_stub_finished", break_op("return", nop()))
            })), nop()))
        }

        self.assertEqual(ast, CORRECT)


    def test_2_local_variables_with_mutation(self):
        ast = parse("""
            function(Void => Void) nothrow noexit {
                Integer foo = 42;
                foo = foo + 3;
                String bar = "hello";
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "argument": type_op("Void"),
                "breaks": new_object_op({
                    "return": type_op("Void")
                }),
                "local": object_type({
                    "foo": type_op("Integer")
                })
            }),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            }),
            "code": comma_op([
                assignment_op(
                    symbolic_dereference_ops(["foo"]),
                    binary_op("addition", symbolic_dereference_ops(["foo"]), literal_op(3))
                ),
                catch_op("function_stub_finished", jump_op(prepare_op(literal_op({
                    "static": new_object_op({
                        "argument": type_op("Void"),
                        "breaks": new_object_op({
                            "all": type_op("Inferred")
                        }),
                        "local": object_type({
                            "bar": type_op("String")
                        })
                    }),
                    "local_initializer": new_object_op({
                        "bar": literal_op("hello")
                    }),
                    "code": break_op("function_stub_finished", break_op("return", nop()))
                })), nop()))
            ])
        }

        self.assertEqual(ast, CORRECT)

class TestObjectTypes(TestCase):
    def test_basic_object(self):
        ast = parse("""
            function(Void => Void) nothrow noexit {
                Object {
                    Integer bar;
                } foo = { bar: 5 };
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Void")
                }),
                "local": object_type({
                    "foo": object_type({
                        "bar": type_op("Integer")
                    })
                }),
                "argument": type_op("Void")
            }),
            "local_initializer": new_object_op({
                "foo": new_object_op({ "bar": literal_op(5) })
            }),
            "code": break_op("return", nop())
        }
        self.assertEqual(ast, CORRECT)

class TestExtraStatic(TestCase):
    def test_extra_statics(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                static foo = 5;
                return foo;
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "local": object_type({}),
                "argument": type_op("Void"),
                "breaks": new_object_op({ "return": type_op("Integer"), "exit": type_op("Integer") }),
                "foo": literal_op(5)
            }),
            "local_initializer": new_object_op({}),
            "code": transform_op(symbolic_dereference_ops(["foo"]), input="value", output="return")
        }
        self.assertEqual(ast, CORRECT)

class TestNestedFunctions(TestCase):

    def test_nested_function(self):
        ast = parse("""
            function(Void => Integer) nothrow noexit {
                Function<Void => Integer> noexit foo = function(Void => Integer) nothrow noexit {
                    return 42;
                };
                return foo();
            }
        """)
        CORRECT = {
            "static": new_object_op({
                "breaks": new_object_op({
                    "return": type_op("Integer")
                }),
                "local": object_type({
                    "foo": function_type(
                        type_op("Void"), {
                            "return": type_op("Integer")
                        }
                    )
                }),
                "argument": type_op("Void")
            }),
            "local_initializer": new_object_op({
                "foo": prepare_op(literal_op({
                    "static": new_object_op({
                        "argument": type_op("Void"),
                        "breaks": new_object_op({ "return": type_op("Integer") }),
                        "local": object_type({})
                    }),
                    "local_initializer": new_object_op({}),
                    "code": break_op("return", literal_op(42))
                }))
            }),
            "code":
                break_op("return",
                    catch_op("return", jump_op(symbolic_dereference_ops(["foo"]), nop()))
                )
        }
        self.assertEqual(ast, CORRECT)



if __name__ == '__main__':
    unittest.main()

