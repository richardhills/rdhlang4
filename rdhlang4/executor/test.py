# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from posix import remove
import unittest
from unittest.case import TestCase

from rdhlang4.executor.executor import PreparedFunction, PreparationException, \
    BreakException, JumpOpcode, DynamicDereferenceOpcode, PrepareOpcode, \
    enforce_application_break_mode_constraints, OPCODES
from rdhlang4.executor.stdlib import add_function
from rdhlang4.parser.rdhparser import parse, prepare_code
from rdhlang4.type_system.core_types import ObjectType, IntegerType, merge_types, \
    RemoveRevConst, are_break_types_equal, ListType, AnyType, StringType
from rdhlang4.type_system.values import Object, List, get_manager
from rdhlang4.utils import NO_VALUE


class TestExecutor(TestCase):
    maxDiff = 65536

    def test_prepare_function(self):
        function = prepare_code("""
            function(Void => Integer) {
                return 42;
            }
        """)
        self.assertEqual(function.invoke(), 42)

    def test_prepare_code(self):
        function = prepare_code("""
            exit 42;
        """)
        self.assertEqual(function.invoke(), 42)

    def test_return_number(self):
        ast = parse("""
            function(Void => Integer) {
                return 42;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

    def test_return_local(self):
        ast = parse("""
            function(Void => Integer) {
                Integer foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

    def test_exec(self):
        function = prepare_code("""
            function(Void => Integer) {
                return exec({
                    "opcode": "addition",
                    "lvalue": {
                        "opcode": "literal",
                        "value": 38
                    },
                    "rvalue": {
                        "opcode": "literal",
                        "value": 4
                    }
                });
            }
        """)
        self.assertEqual(function.invoke(), 42)

    def test_code(self):
        function = prepare_code("""
            function(Void => Integer) {
                return exec({
                    "opcode": "addition",
                    "lvalue": code( 34 + 4 ),
                    "rvalue": code( 4 )
                });
            }
        """)
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

    def test_object_mutations(self):
        ast = parse("""
            function(Void => Integer) {
                Object { Integer bar; } foo = { bar: 5 };
                foo.bar = foo.bar + 36;
                return foo.bar + 1;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

    def test_weak_unchecked_object_mutations(self):
        ast = parse("""
            function(Void => Integer) {
                Object { Any bar; } foo = { bar: 5 };
                foo.bar = foo.bar + 36;
                return foo.bar + 1;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

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

    def test_empty_list_instantiation(self):
        code = prepare_code("""
            function() nothrow {
                Tuple<Integer, Integer> t = [ 4, 23 ];
                List<Integer> l = [];
            }
        """)
        code.invoke()

    def test_list1(self):
        code = prepare_code("""
            function() {
                List<Integer> l = [ 42 ];
                return l[0];
            }
        """)
        self.assertEquals(code.invoke(), 42)

    def test_list2(self):
        code = prepare_code("""
            function() nothrow {
                Tuple<Integer> l = [ 42 ];
                return l[0];
            }
        """)
        self.assertEquals(code.invoke(), 42)

    def test_list3(self):
        code = prepare_code("""
            function() nothrow {
                Tuple<Integer, Integer> f = [ 30, 12 ];
                return f[0] + f[1];
            }
        """)
        self.assertEqual(code.invoke(), 42)

    def test_list4(self):
        code = prepare_code("""
            function() nothrow {
                Tuple<Integer> l = [ 12 ];
                l[0] = 42;
                return l[0];
            }
        """)
        self.assertEquals(code.invoke(), 42)

    def test_list_coveriance(self):
        code = prepare_code("""
            function() {
                List<Integer> l = [ 42 ];
                List<const Any> a = l;
                return l[0];
            }
        """)
        self.assertEquals(code.invoke(), 42)

    def test_list_tuple_coveriance(self):
        code = prepare_code("""
            function() {
                Tuple<Integer> l = [ 42 ];
                List<const Integer> a = l;
                return l[0];
            }
        """)
        self.assertEquals(code.invoke(), 42)

    def test_python_like_code(self):
        ast = parse("""
            function(Void => Any) {
                foo = 42;
                return foo;
            }
        """)
        function = PreparedFunction(ast)
        self.assertTrue(isinstance(function.break_types["exception"], ObjectType))
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 42)

    def test_python_object_property(self):
        ast = prepare_code("""
            z = {};
            z.qqq=123;
        """)
        ast.invoke()

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
        self.assertEqual(function.invoke(), 42)

    def test_inferred_empty_object_type(self):
        function = prepare_code("""
            function() {
                var foo = {};
            }
        """)
        self.assertEqual(function.invoke(), NO_VALUE)

    def test_inferred_simple_object_type(self):
        return;
        function = prepare_code("""
            function() {
                var foo = { bar: 123 };
                foo.bar = 42;
                return foo.bar;
            }
        """)
        self.assertEqual(function.invoke(), 42)

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
        self.assertEqual(function.invoke(), 12)

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
        self.assertEqual(function.invoke(), ((5 ** 2) ** 2) ** 2)

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
        self.assertEqual(function.invoke(), ((5 ** 2) ** 2) ** 2)

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
        self.assertTrue(are_break_types_equal(
            function.break_types, { "return": IntegerType(), "exit": IntegerType() })
        )
        self.assertEqual(function.invoke(), ((5 ** 2) ** 2) ** 2)


class TestExtraStatics(TestCase):

    def test_extra_statics(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                static bam = 42;
                return bam;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

    def test_static_type(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                static Foo = Object { Integer bar; };
                Foo foo = { bar: 42 };
                return foo.bar;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)

    def test_typedef_type(self):
        ast = parse("""
            function(Void => Integer) nothrow {
                typedef Object { Integer bar; } Foo;
                Foo foo = { bar: 42 };
                return foo.bar;
            }
        """)
        function = PreparedFunction(ast)
        self.assertEqual(function.invoke(), 42)


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


class TestImport(TestCase):

    def test_import(self):
        function = prepare_code("""
            import requests;
            var response = requests.get({ kwargs: { url: "https://news.bbc.co.uk/" }});
            return response.status_code == 200;
        """)

        expected = merge_types([
            JumpOpcode.PYTHON_EXCEPTION.get_type().visit(RemoveRevConst()),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type().visit(RemoveRevConst()),
            OPCODES["equals"].MISSING_INTEGERS.get_type().visit(RemoveRevConst())
        ])

        # self.assertTrue(expected.is_copyable_from(function.break_types["exception"], {}))

        self.assertEqual(function.invoke(), True)


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
        function = prepare_code("""foo = function(Void => Integer) {};""", check_application_break_mode_constraints=False);

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type(),
        ])

        self.assertTrue(function.break_types["exception"].is_copyable_from(expected, {}))

        with self.assertRaises(BreakException):
            function.invoke()
 
    def test5(self):
        function = prepare_code("""foo = function(Void => Integer) {}; foo();""", check_application_break_mode_constraints=False)

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            JumpOpcode.INVALID_ARGUMENT.get_type(),
            JumpOpcode.MISSING_FUNCTION.get_type(),
            JumpOpcode.UNKNOWN_BREAK_MODE.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type()
        ])

        self.assertTrue(function.break_types["exception"].is_copyable_from(expected, {}))

        with self.assertRaises(BreakException):
            function.invoke()

    def test6(self):
        function = prepare_code("""foo = function(Void => Integer) { return "hello"; }; foo();""", check_application_break_mode_constraints=False)

        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            JumpOpcode.INVALID_ARGUMENT.get_type(),
            JumpOpcode.MISSING_FUNCTION.get_type(),
            JumpOpcode.UNKNOWN_BREAK_MODE.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type()
        ])

        self.assertTrue(function.break_types["exception"].is_copyable_from(expected, {}))

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

        self.assertEqual(function.invoke(), "hello")

    def test10(self):
        function = prepare_code("""
            bam = function(Void => Integer) {
                foo = 123;
                bar = foo * 233 + foo;
                return bar;
            };
            bam();
        """, check_application_break_mode_constraints=False)
        expected = merge_types([
            PrepareOpcode.PREPARATION_ERROR.get_type(),
            JumpOpcode.INVALID_ARGUMENT.get_type(),
            JumpOpcode.MISSING_FUNCTION.get_type(),
            JumpOpcode.UNKNOWN_BREAK_MODE.get_type(),
            DynamicDereferenceOpcode.INVALID_DEREFERENCE.get_type()
        ])
        self.assertTrue(function.break_types["exception"].is_copyable_from(expected, {}))
        with self.assertRaises(BreakException):
            function.invoke()

    def test11(self):
        function = prepare_code("""
            typedef Integer Foo;
            typedef String Baz;
            typedef Object { Integer foo; } Bar;
            Foo foo = 123;
            Baz baz = "hello";
            Bar b = { foo: 123 };
            return foo;
        """)
        self.assertEqual(function.invoke(), 123);

    def test12(self):
        function = prepare_code("""
        {
            "static": {
              "opcode": "new_object",
              "properties": {
                "breaks": {
                  "opcode": "new_object",
                  "properties": {
                    "return": {
                      "opcode": "new_object",
                      "properties": {
                        "type": { "opcode": "literal", "value": "Unit" },
                        "value": { "opcode": "literal", "value": 123 }
                      }
                    }
                  }
                }
              }
            },
            "code": {
              "opcode": "transform",
              "output": "return",
              "input": "value",
              "code": { "opcode": "literal", "value": 123 }
            }
        }
        """)
        self.assertEqual(function.invoke(), 123);

    def test13(self):
        # Generally an invalid program, because it might exit with a non-integer
        function = prepare_code("""
            var boo = function() {
            };
            exit boo();
        """, check_application_break_mode_constraints=False)
        self.assertEqual(function.invoke(), NO_VALUE);

    def test14(self):
        function = prepare_code("""
            var foo = function(String) {
                return { type: argument };
            };

            var bar = dynamic function(foo("Integer") => Integer) {
               return argument + 1;
            };

            return bar(41);
        """, check_application_break_mode_constraints=False)
        self.assertEqual(function.invoke(), 42);

    def test15(self):
        function = prepare_code("""
            function() {
              Tuple<Integer> foo = [ 1, 2 ];
              return foo[1];
            }
        """)
        self.assertEquals(function.invoke(), 2)

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
#         self.assertEqual(function.invoke(), 233168)

#     def testProblem1b(self):
#         function = prepare_code("""
#             exit sum( [ i for i in range(1000) if i % 3 == 0 and i % 5 == 0 ] );
#         """)
#         self.assertEqual(function.invoke(), 233168)

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
        self.assertEqual(function.invoke(), 4613732)

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
        self.assertEqual(function.invoke(), 6857)

set_first_list_element = prepare_code("""
    function(Any) {
        return dynamic function(Tuple<Tuple<outer.argument>, outer.argument>) nothrow noexit {
            argument[0][0] = argument[1];
            return;
        };
    }
""", check_application_break_mode_constraints=False)

broken_argument_set_first_list_element = prepare_code("""
    function(Any) {
        return dynamic function(Tuple<Tuple<outer.argument>, Integer>) nothrow noexit {
            argument[0][0] = argument[1];
            return;
        };
    }
""", check_application_break_mode_constraints=False)

class TestDynamicFunctions(TestCase):
    def test_set_element_integer(self):
        numbers = List([ 4, 5 ])
        get_manager(numbers).create_reference(ListType([], IntegerType(), False), False)

        integer_set_function = set_first_list_element.invoke(Object({ "type": "Integer" }))
        integer_set_function.invoke(List([ numbers, 42 ]))

        self.assertEqual(numbers, List([ 42, 5 ]))

    def test_set_element_string(self):
        words = List([ "hello", "world" ])
        get_manager(words).create_reference(ListType([], StringType(), False), False)

        string_set_function = set_first_list_element.invoke(Object({ "type": "String" }))
        string_set_function.invoke(List([ words, "hi" ]))

        self.assertEqual(words, List([ "hi", "world" ]))

    def test_broken_works_with_int_set_element_string(self):
        numbers = List([ 4, 5 ])
        get_manager(numbers).create_reference(ListType([], IntegerType(), False), False)

        integer_set_function = set_first_list_element.invoke(Object({ "type": "Integer" }))
        integer_set_function.invoke(List([ numbers, 42 ]))

        self.assertEqual(numbers, List([ 42, 5 ]))

    def test_broken_set_element_string(self):
        words = List([ "hello", "world" ])
        get_manager(words).create_reference(ListType([], StringType(), False), False)

        with self.assertRaises(BreakException):
            broken_argument_set_first_list_element.invoke(Object({ "type": "String" }))

    def test_other_constraint_breaks_dynamic_function(self):
        words = List([ "hello", "world" ])
        get_manager(words).create_reference(ListType([], AnyType(), False), False)

        string_set_function = set_first_list_element.invoke(Object({ "type": "String" }))
        with self.assertRaises(BreakException):
            string_set_function.invoke(List([ words, "hi" ]))

class TestGenericDereferences(TestCase):
    def test_adder_function(self):
        code = prepare_code("""
            function() {
                List<Integer> foo = [ 1, 2, 3 ];

                Function<Integer => Void> adder = foo.add;

                adder(4);

                return foo[0] + foo[1] + foo[2] + foo[3];
            }
        """)
        self.assertEquals(code.invoke(), 10)

class TestStaticOperator(TestCase):
    def test_run_time_arithmatic(self):
        code = prepare_code("""
            var x = <5 * 8 + 2>;
            exit x;
        """)
        self.assertEquals(code.invoke(), 42)

    def test_call_static_function(self):
        code = prepare_code("""
            static x = function(Integer) { return argument + 1; };
            return x<41>;
        """)
        self.assertEquals(code.invoke(), 42)


    def test_call_static_function2(self):
        code = prepare_code("""
            static square = function(Integer) { return argument * argument; };
            Integer x1 = <square<6> + <6>>;
            Integer x2 = <square(6) + <6>>;
            Integer x3 = <square<6> + 6>;
            Integer x4 = <square(6) + 6>;
            Integer x5 = square<6> + <6>;
            Integer x6 = square(6) + <6>;
            Integer x7 = square<6> + 6;
            Integer x8 = square(6) + 6;
            exit [ x1, x2, x3, x4, x5, x6, x7, x7, x8 ];
        """, check_application_break_mode_constraints=False)
        EXPECTED = [ 42, 42, 42, 42, 42, 42, 42, 42, 42 ]
        result = code.invoke()
        self.assertEquals(result, EXPECTED)

    def test_call_static_function3(self):
        code = prepare_code("""
            static square = function(Integer) { return argument * argument; };
            var x1 = <square<6> + <6>>;
            var x2 = <square(6) + <6>>;
            var x3 = <square<6> + 6>;
            var x4 = <square(6) + 6>;
            var x5 = square<6> + <6>;
            var x6 = square(6) + <6>;
            var x7 = square<6> + 6;
            var x8 = square(6) + 6;
            exit [ x1, x2, x3, x4, x5, x6, x7, x7, x8 ];
        """, check_application_break_mode_constraints=False)
        EXPECTED = [ 42, 42, 42, 42, 42, 42, 42, 42, 42 ]
        result = code.invoke()
        self.assertEquals(result, EXPECTED)

    def test_mixture_of_runtime_and_verification_time(self):
        code = prepare_code("""
            static x = function(Integer) { return argument + 1; };
            static a = x<10>;
            static b = x(10);
            var c = x<10>;
            var d = x<10>;
            exit a + b + c + d + x(10) + x<10>;
        """)
        self.assertEquals(code.invoke(), 66)


class TestStaticStdLib(TestCase):
    def test_add_function_created_in_statics(self):
        code = prepare_code("""
            List<Integer> foo = [ 38 ];
            static Adder = add(Integer);
            Adder([ foo, 4 ]);
            exit foo[0] + foo[1];
        """)
        self.assertEquals(code.invoke(), 42)

    def test_add_function_created_with_static_opcode(self):
        code = prepare_code("""
            List<Integer> foo = [ 38 ];
            add<Integer>([ foo, 4 ]);
            exit foo[0] + foo[1];
        """)
        self.assertEquals(code.invoke(), 42)

if __name__ == '__main__':
    unittest.main()

