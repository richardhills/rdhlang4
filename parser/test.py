# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import unittest
from unittest.case import TestCase

from parser.rdhparser import parse
from parser.visitor import comma_op, literal_op, break_op, addition_op, \
    object_type, function_type, prepare_op, function, new_object_op, \
    assignment_op, invoke_ops, dereference_op, type, merge_op, function_literal, \
    catch_op, jump_op
import ast
from _ast import AST


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
            function () { }
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
            function() { local = 42; }
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
                dereference_op("local"),
                literal_op(42)
            )
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

    def test_simple_return_function(self):
        ast = parse("""
            function() { return 42; }
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

        self.assertEquals(ast, CORRECT)

    def test_simple_return_function_with_types(self):
        ast = parse("""
            function(String => Integer) { return 42; }
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
            function() { 4 + 38; }
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
            function(Void => Void) {
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
            function(Void => Integer) {
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
            "code": break_op("return", dereference_op("foo")),
            "local_initializer": new_object_op({
                "foo": literal_op(42)
            })
        }
        print json.dumps(ast)
        print json.dumps(CORRECT)
        self.assertEquals(ast, CORRECT)

    def test_2_local_variables(self):
        ast = parse("""
            function(Void => Void) {
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
                    "foo": type("Integer"),
                    "bar": type("String")
                })
            }),
            "local_initializer": merge_op(
                catch_op("local_initialized",
                    jump_op(prepare_op(literal_op(function_literal(
                        type("Void"),
                        merge_op(
                            new_object_op({
                                "return": type("Void")
                            }),
                            new_object_op({
                                "local_initialized": object_type({
                                    "foo": type("Integer")    
                                })
                            })
                        ),
                        object_type({
                            "foo": type("Integer")
                        }),
                        new_object_op({ "foo": literal_op(42) }), [
                            break_op("local_initialized", dereference_op("local"))
                        ]
                    ))),
                    None)
                ),
                new_object_op({
                    "bar": literal_op("hello")
                })
            )
        }

        self.assertEquals(ast, CORRECT)


    def test_2_local_variables_with_mutation(self):
        ast = parse("""
            function(Void => Void) {
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
                    "foo": type("Integer"),
                    "bar": type("String")
                })
            }),
            "local_initializer": merge_op(
                catch_op("local_initialized",
                    jump_op(prepare_op(literal_op(function_literal(
                        type("Void"),
                        merge_op(
                            new_object_op({
                                "return": type("Void")
                            }),
                            new_object_op({
                                "local_initialized": object_type({
                                    "foo": type("Integer")    
                                })
                            })
                        ),
                        object_type({
                            "foo": type("Integer")
                        }),
                        new_object_op({ "foo": literal_op(42) }),
                        [
                            assignment_op(dereference_op("foo"),
                                addition_op(
                                    dereference_op("foo"),
                                    literal_op(3)
                                )
                            ),
                            break_op("local_initialized", dereference_op("local"))
                        ]
                    ))),
                    None)
                ),
                new_object_op({
                    "bar": literal_op("hello")
                })
            )
        }

        print json.dumps(ast)
        print json.dumps(CORRECT)

        self.assertEquals(ast, CORRECT)


class TestNestedFunctions(TestCase):

    def test_nested_function(self):
        return
        ast = parse("""
            function(Void => Integer) {
                Function<Void => Integer> foo = function(Void => Integer) {
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
            "code": comma_op([
                assignment_op(
                    literal_op("foo"),
                    literal_op("compound"),
                    prepare_op(literal_op(function(
                        type("Void"), type("Integer"), [
                            break_op("local_initialized", literal_op(42))
                        ]
                    )))
                ),
                break_op("return",
                    invoke_ops(
                        dereference_op("foo")
                    )
                )
            ])
        }
        self.assertEquals(ast, CORRECT)



if __name__ == '__main__':
    unittest.main()

