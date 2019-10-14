# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from unittest.case import TestCase

from executor.executor import PreparedFunction, PreparationException
from parser.rdhparser import parse


class TestExecutor(TestCase):
    maxDiff = 65536

    def test_return_number(self):
        ast = parse("""
            function(Void => Integer) {
                return 42;
            }
        """)
        print json.dumps(ast)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_invalid_return_type(self):
        ast = parse("""
            function(Void => String) {
                return 42;
            }
        """)
        with self.assertRaises(PreparationException):
            PreparedFunction(ast)

    def test_basic_addition(self):
        ast = parse("""
            function(Void => Integer) {
                return 38+4;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_return_local(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_simple_chained_return_local(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                Integer bar = foo;
                Integer baz = bar;
                return baz;
            }
        """)
        print json.dumps(ast)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)


    def test_complex_chained_return_local(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 40;
                Integer bar = foo + 1;
                Integer baz = bar + 1;
                return baz;
            }
        """)
        print json.dumps(ast)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)


    def test_invalid_assignment(self):
        ast = parse("""
            function(Void => String) {
                String foo = 42;
                return foo;
            }
        """)
        with self.assertRaises(PreparationException):
            PreparedFunction(ast)

    def test_nested_function_call(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Void => Integer> foo = function(Void => Integer) {
                    return 42;
                };
                return foo();
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_outer_context_access(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                Function<Void => Integer> baz = function(Void => Integer) {
                    return foo;
                };
                return baz();
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)


    def test_argument_access(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Integer => Integer> incremented = function(Integer => Integer) {
                    return argument + 1;
                };
                return incremented(41);
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_object_mutations(self):
        ast = parse("""
            function(Void => Integer) {
                Object { Integer bar; } foo = { bar: 5 };
                foo.bar = foo.bar + 36;
                return foo.bar + 1;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_doubler(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Integer => Integer> doubler = function(Integer => Integer) {
                    return argument + argument;
                };
                Function<Object {
                    Function<Integer => Integer> func;
                    Integer number;
                } => Integer> doItTwice = function(Object {
                    Function<Integer => Integer> func;
                    Integer number;
                } => Integer) {
                    return func(func(number));
                };
                return doItTwice({ func: doubler, number: 3 });
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 12)

    def test_monad(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Void => Integer> fiver = function(Void => Integer) {
                    return 5;
                };
                Function<Function<Void => Integer> => Function<Void => Integer>> squarer =
                    function(Function<Void => Integer> => Function<Void => Integer>) {
                        return function(Void => Integer) {
                            return outer.argument() * outer.argument();
                        };
                };
                return squarer(squarer(squarer(fiver)))();
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 5 * 5 * 5 * 5 * 5 * 5 * 5 * 5)

