# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from unittest.case import TestCase

from rdhlang4.executor.executor import PreparedFunction, PreparationException, \
    BreakException, JumpOpcode, DynamicDereferenceOpcode, PrepareOpcode, \
    enforce_application_break_mode_constraints
from rdhlang4.parser.rdhparser import parse, prepare_code
from rdhlang4.type_system.core_types import ObjectType, IntegerType, merge_types


class TestExecutor(TestCase):
    maxDiff = 65536

    def test_prepare_function(self):
        function = prepare_code("""
            function(Void => Integer) {
                return 42;
            }
        """)
        self.assertEquals(function.invoke(), 42)

    def test_prepare_code(self):
        function = prepare_code("""
            exit 42;
        """)
        self.assertEquals(function.invoke(), 42)


    def test_return_number(self):
        ast = parse("""
            function(Void => Integer) {
                return 42;
            }
        """)
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
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)


    def test_invalid_assignment(self):
        ast = parse("""
            function(Void => String) nothrow {
                String foo = 42;
                return foo;
            }
        """)
        with self.assertRaises(PreparationException):
            PreparedFunction(ast)

    def test_nested_function_call(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Void => Integer> foo = function(Void => Integer) nothrow {
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
                Function<Void => Integer> baz = function(Void => Integer) nothrow {
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
                Function<Integer => Integer> incremented = function(Integer => Integer) nothrow {
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

    def test_weak_unchecked_object_mutations(self):
        ast = parse("""
            function(Void => Integer) {
                Object { Any bar; } foo = { bar: 5 };
                foo.bar = foo.bar + 36;
                return foo.bar + 1;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_weak_checked_object_mutations(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                Object { Any bar; } foo = { bar: 5 };
                foo.bar = foo.bar + 36;
                return foo.bar + 1;
            }
        """)
        with self.assertRaises(PreparationException) as cm:
            PreparedFunction(ast)

    def test_python_like_code(self):
        ast = parse("""
            function(Void => Any) {
                foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertTrue(isinstance(function.break_types["exception"], ObjectType))
        self.assertEquals(function.invoke(), 42)

    def test_python_reassignment_code(self):
        ast = parse("""
            function(Void => Any) {
                foo = "hello world";
                foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertTrue(isinstance(function.break_types["exception"], ObjectType))
        self.assertEquals(function.invoke(), 42)

    def test_broken_assignment(self):
        ast = parse("""
            function(Void => Any) {
                String foo = "hello world";
                foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        with self.assertRaises(BreakException):
            function.invoke()

    def test_inferred_primitive_types(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                var foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)
 

    def test_doubler(self):
        ast = parse("""
            function(Void => Integer) {
                Function<Integer => Integer> doubler = function(Integer => Integer) nothrow {
                    return argument + argument;
                };
                Function<Object {
                    Function<Integer => Integer> func;
                    Integer number;
                } => Integer> doItTwice = function(Object {
                    Function<Integer => Integer> func;
                    Integer number;
                } => Integer) nothrow {
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
        self.assertEquals(function.invoke(), ((5 ** 2) ** 2) ** 2)

    def test_monad_with_typedef(self):
        ast = parse("""
            function(Void => Integer) {
                typedef Function<Void => Integer> IntMaker;
                IntMaker fiver = function(Void => Integer) {
                    return 5;
                };

                typedef Function<IntMaker => IntMaker> IntMakerModifier;
                IntMakerModifier squarer = function(IntMaker => IntMaker) {
                    return function(Void => Integer) {
                        return outer.argument() * outer.argument();
                    };
                };

                IntMaker newfunction = squarer(squarer(squarer(fiver)));
                return newfunction();
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), ((5 ** 2) ** 2) ** 2)

    def test_monad_with_inferred_types(self):
        ast = parse("""
            function() {
                var fiver = function() {
                    return 5;
                };

                var squarer = function(Function<Void => Integer>) {
                    return function() {
                        return outer.argument() * outer.argument();
                    };
                };

                var fiverSquaredOverAndOver = squarer(squarer(squarer(fiver)));

                return fiverSquaredOverAndOver();
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.break_types, { "return": IntegerType(), "exit": IntegerType() })
        self.assertEquals(function.invoke(), ((5 ** 2) ** 2) ** 2)

class TestExtraStatics(TestCase):
    def test_extra_statics(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                static bam = 42;
                return bam;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_static_type(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                static Foo = Object { Integer bar; };
                Foo foo = { bar: 42 };
                return foo.bar;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)

    def test_typedef_type(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                typedef Object { Integer bar; } Foo;
                Foo foo = { bar: 42 };
                return foo.bar;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEquals(function.invoke(), 42)



class TestPreparationErrors(TestCase):
    def test_invalid_code_fail_at_preparation(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                Integer foo = "hello";
                return foo;
            }
        """)
        with self.assertRaises(PreparationException) as cm:
            PreparedFunction(ast)

    def test_invalid_code_with_inferred_throws_fails_at_runtime(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = "hello";
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        with self.assertRaises(BreakException) as cm:
            function.invoke()

    def test_invalid_code_with_throws_all_fails_at_runtime(self):
        ast = parse("""
            function(Void => Integer) throws Any {
                Integer foo = "hello";
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        with self.assertRaises(BreakException) as cm:
            function.invoke()

class TestMiscelaneous(TestCase):
    # Tests I've found don't work when playing.
    def test1(self):
        function = prepare_code("""foo = function() {};""");
        function.invoke()
 
    def test2(self):
        function = prepare_code("""var foo = function() {};""");
        function.invoke()
 
    def test3(self):
        function = prepare_code("""
            var func = function() { };
            return func(42);
        """)
        with self.assertRaises(BreakException):
            function.invoke()

    def test4(self):
        function = prepare_code("""foo = function(Void => Integer) {};""");

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type(),
        ])

        self.assertTrue(expected.is_copyable_from(function.break_types["exception"]))

        with self.assertRaises(BreakException):
            function.invoke()
 
    def test5(self):
        function = prepare_code("""foo = function(Void => Integer) {}; foo();""")

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            JumpOpcode.INVALID_ARGUMENT.get_type(),
            JumpOpcode.MISSING_FUNCTION.get_type(),
            JumpOpcode.UNKNOWN_BREAK_MODE.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type()
        ])

        self.assertTrue(expected.is_copyable_from(function.break_types["exception"]))

        with self.assertRaises(BreakException):
            function.invoke()

    def test6(self):
        function = prepare_code("""foo = function(Void => Integer) { return "hello"; }; foo();""")

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            JumpOpcode.INVALID_ARGUMENT.get_type(),
            JumpOpcode.MISSING_FUNCTION.get_type(),
            JumpOpcode.UNKNOWN_BREAK_MODE.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type()
        ])

        self.assertTrue(expected.is_copyable_from(function.break_types["exception"]))

        with self.assertRaises(BreakException):
            function.invoke()

    def test7(self):
        function = prepare_code("""
            var incremented = function(Integer) nothrow {
                return argument + 1;
            };
            incremented(41);
        """)
        self.assertEqual(function.invoke(), 42)

    def test8(self):
        function = prepare_code("""
            f = function(Any) {
                return argument;
            };

            return f();
        """)
        with self.assertRaises(BreakException):
            function.invoke()

    def test9(self):
        function = prepare_code("""
            foo = "hello";
            foo = return foo;
        """)

        self.assertEquals(function.invoke(), "hello")

    def test10(self):
        function = prepare_code("""
            bam = function(Void => Integer) {
                foo =123;
                bar = foo * 233 + foo;
                return bar;
            };
            bam();
        """)
        #self.assertNotEquals(function.break_types["exception"]["property_types"]["message"].value, "")
        # Fails with PreparationError at run time which isn't caught at compile time

    def test11(self):
        return
        function = prepare_code("""
            typedef Integer Foo;
            typedef String Baz;
            typedef { foo: Integer } Bar;
            Foo foo = 123;
            Baz baz = "hello";
            Bar b = { foo: 123 };
            return foo;
        """)

class TestEuler(TestCase):
#     def testProblem1a(self):
#         function = prepare_code("""
#             var answer = 1;
#             for(var i in range(1000)) {
#                 if(i % 3 == 0 and i % 5 == 0) {
#                     answer = answer * i;
#                 }
#             }
#             return i;
#         """)
#         self.assertEquals(function.invoke(), 233168)


#     def testProblem1b(self):
#         function = prepare_code("""
#             exit sum( [ i for i in range(1000) if i % 3 == 0 and i % 5 == 0 ] );
#         """)
#         self.assertEquals(function.invoke(), 233168)

    def testProblem2(self):
        function = prepare_code("""
            var a = 1, b = 2;
            var answer = 0;
            while(b <= 4000000) {
                if(b % 2 == 0) {
                    answer = answer + b;
                };
                var z = a + b;
                a = b;
                b = z;
            };
            exit answer;
        """)
        enforce_application_break_mode_constraints(function)
        self.assertEquals(function.invoke(), 4613732)

    def testProblem3(self):
        function = prepare_code("""
            var test = 2, target = 600851475143;
            var current = target;
            while(current != 1) {
                if(current % test == 0) {
                    current = current / test;
                } else {
                    test = test + 1;
                };
            };
            exit test;
        """)
        enforce_application_break_mode_constraints(function)
        self.assertEquals(function.invoke(), 6857)