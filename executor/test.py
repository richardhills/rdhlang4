# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from unittest.case import TestCase

from executor.executor import FunctionExecutor, PreparationException
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
        function = FunctionExecutor(ast)
        self.assertEquals(function.invoke(), 42)

    def test_invalid_return_type(self):
        ast = parse("""
            function(Void => String) {
                return 42;
            }
        """)
        with self.assertRaises(PreparationException):
            FunctionExecutor(ast)

    def test_basic_addition(self):
        ast = parse("""
            function(Void => Integer) {
                return 38+4;
            }
        """)
        function = FunctionExecutor(ast)
        self.assertEquals(function.invoke(), 42)

    def test_return_local(self):
        return
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                return foo;
            }
        """)
        function = FunctionExecutor(ast)
        self.assertEquals(function.invoke(), 42)

    def test_chained_return_local(self):
        return False
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                Integer bar = foo;
                Integer baz = bar;
                return baz;
            }
        """)
        print json.dumps(ast)
        function = FunctionExecutor(ast)
        self.assertEquals(function.invoke(), 42)


    def test_invalid_assignment(self):
        ast = parse("""
            function(Void => String) {
                String foo = 42;
                return foo;
            }
        """)
        with self.assertRaises(PreparationException):
            FunctionExecutor(ast)
