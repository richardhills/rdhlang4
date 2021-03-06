# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from unittest.case import TestCase
import unittest.main

from bunch import bunchify
from munch import munchify

from rdhlang4.exception_types import CreateReferenceError, IncompatableAssignmentError
from rdhlang4.type_system.core_types import merge_types, \
    OneOfType, ObjectType, IntegerType, BooleanType, AnyType, UnitType, \
    are_bindable, StringType, ListType, NoValueType, NoType
from rdhlang4.type_system.values import Object, List, get_manager, \
    create_crystal_type


# Golden rules:
# At compile time, be conservative. Block anything that might allow me to break someone else, or might allow someone else to break me.
# At runtime, be liberal. Block only things that we know will either break us or something else, using the greater amount of information to hand.
#
# Modifiers, like const, allow more types of assignment, because the range of things that might break is reduced
class TestCompileTimeObjectChecks(TestCase):
    maxDiff = 65536

    def test_successful_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_with_different_types_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        }, False)

        # This fails because it would allow me to do:
        # foo.baz = True
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_failed_covariant_with_different_types_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": AnyType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        }, False)

        # This fails because it would allow me to do:
        # foo.baz = "hello, how are you"
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_covariant_with_different_types_and_const_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": AnyType(is_const=True)
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        }, False)

        # Like the previous case, but with foo.baz explicitely blocked by const
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_successful_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType(),
            "bam": IntegerType()
        }, False)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_covariant_with_extra_fields_compile_time_object_initialization(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType(),
            "bam": IntegerType()
        }, False)

        # This fails because foo and bar are now names for the same reference,
        # so foo = { "bar": 2, "baz": True } will work, breaking other_foo
        self.assertFalse(are_bindable(foo, other_foo, False, False, {}))

    def test_failed_contraviant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType(),
            "bam": IntegerType()
        }, False)

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        }, False)

        # This fails because it would allow me to do:
        # foo.bam - which is undefined
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_with_different_types_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": BooleanType()
            }, False)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # This fails because it would allow me to do:
        # foo.bar.baz = True
        # OR
        # foo.bar = { baz: True }
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_failed_covariant_with_different_types_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, False)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # This fails because it would allow me to do:
        # foo.bar.baz = "hello, how are you?"
        # OR
        # foo.bar = { baz: "wazup?" }
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_failed_covariant_with_different_types_and_partial_const1_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, False, is_const=True)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # This fails because it would allow me to do:
        # foo.bar.baz = "hello, how are you?"
        # ... although this is blocked:
        # foo.bar = { baz: "wazup?" }
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_failed_covariant_with_different_types_and_partial_const2_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, False, is_const=True)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # This fails because it would allow me to do:
        # foo.bar = { baz: "wazup?" }
        # ... but this would be blocked...
        # foo.bar.baz = "hello, how are you?"
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_covariant_with_different_types_and_const_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType(is_const=True)
            }, False, is_const=True)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # Like the previous 3 cases, but the 2 error cases are both blocked explicitely by the const
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_nesting_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            }, False)
        }, False)

        # This fails because it would allow me to do
        # foo.bar = { "baz": 123 }
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_succeeded_nesting_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False, is_const=True)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            }, False)
        }, False)

        # Like the previous case, but with foo.bar = ... blocked by the const
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_nesting_contravariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            }, False)
        }, False)

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)

        # This fails because it would allow me to do
        # foo.bar.bam - which is undefined
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

class TestTypeRepr(TestCase):
    def test_int_repr(self):
        self.assertEqual(repr(IntegerType()), "IntegerType")

    def test_object_repr(self):
        self.assertEqual(
            repr(ObjectType({ "foo": IntegerType() }, False)),
            """ObjectType<
  foo: IntegerType
>
"""
        )

    def test_nested_object_repr(self):
        self.assertEqual(
            repr(ObjectType({ "foo": ObjectType({ "bar": IntegerType() }, False) }, False)),
            """ObjectType<
  foo: ObjectType<
    bar: IntegerType
  >
>
"""
        )

    def test_recursive_object_repr(self):
        foo = ObjectType({}, False)
        foo.property_types["foo"] = foo

        self.assertEqual(
            repr(foo),
            """ObjectType<
  foo: ObjectType<...>
>
"""
        )

class TestCrystalTypes(TestCase):
    def test_create_crystal_type(self):
        foo = munchify({ "bar": 123 })
        crystal_type = create_crystal_type(foo, False, None, False)
        expected = ObjectType({ "bar": UnitType(123) }, False)

        self.assertTrue(are_bindable(crystal_type, expected, False, False, {}))

    def test_create_nested_crystal_type(self):
        foo = munchify({ "bar": { "foo": 123 } })
        crystal_type = create_crystal_type(foo, False, None, False)
        expected = ObjectType({ "bar": ObjectType({ "foo": UnitType(123) }, False) }, False)

        self.assertTrue(are_bindable(crystal_type, expected, False, False, {}))

    def test_create_recursive_crystal_type(self):
        foo = munchify({ "bar": { } })
        foo.bar.foo = foo
        crystal_type = create_crystal_type(foo, False, None, False)

        Foo = ObjectType({ "bar": ObjectType({ }, False) }, False)
        Foo.property_types["bar"].property_types["foo"] = Foo

        expected = Foo

        self.assertTrue(are_bindable(crystal_type, expected, False, False, {}))

class TestCompileTimeListChecks(TestCase):
    maxDiff = 65536

    def test_successful_simple_compile_time_list_assignment(self):
        foo = ListType([], IntegerType(), False)
        other_foo = ListType([], IntegerType(), False)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_simple_compile_time_list_assignment(self):
        foo = ListType([], AnyType(), False)
        other_foo = ListType([], IntegerType(), False)

        # Blocked because it would allows foo[0] = "hello" - looking at you Java
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_simple_rev_const_compile_time_list_assignment(self):
        foo = ListType([], AnyType(), False)
        other_foo = ListType([], IntegerType(), True)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_successful_simple_compile_time_tuple_assignment(self):
        foo = ListType([ IntegerType(), StringType() ], AnyType(), False)
        other_foo = ListType([ IntegerType(), StringType() ], AnyType(), False)

        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_simple_compile_time_tuple_to_list_assignment(self):
        foo = ListType([], AnyType(), False)
        other_foo = ListType([ IntegerType(), StringType() ], NoType(), False)

        # Blocked because it would allow foo[0] = "hello";
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_simple_compile_time_rev_const_tuple_to_list_assignment(self):
        foo = ListType([], AnyType(), False)
        other_foo = ListType([ IntegerType(), StringType() ], NoType(), True)

        # Allowed because other_foo is rev const, so foo[0] = "hello" wont break it
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_incompatible_type_compile_time_tuple_to_list_assignment(self):
        foo = ListType([], IntegerType(), False)
        other_foo = ListType([ IntegerType(), StringType() ], NoType(), True)

        # Blocked because it would allow foo[1] = 42
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_type_compile_time_same_type_tuple_to_list_assignment(self):
        foo = ListType([], IntegerType(), False)
        other_foo = ListType([ IntegerType(), IntegerType() ], NoType(), False)

        # Allowed because foo.add(1) wont break the rev_const other_foo
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_incompatible_type_list_to_tuple_assignment(self):
        foo = ListType([IntegerType(), IntegerType(), IntegerType()], IntegerType(), False)
        other_foo = ListType([], IntegerType(), False)

        # Blocked because other_foo[0] might fail, but foo[0] can not
        self.assertFalse(foo.is_copyable_from(other_foo, {}))

    def test_successful_truncated_tuple(self):
        foo = ListType([IntegerType()], NoType(), False)
        other_foo = ListType([IntegerType(), IntegerType(), IntegerType()], NoType(), False)

        # Allowed because foo.add, foo.slice etc can be blocked on tuples, and
        # other_foo provides more than enough values for foo
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def test_failed_truncated_tuple(self):
        foo = ListType([IntegerType(), IntegerType(), IntegerType()], NoType(), False)
        other_foo = ListType([IntegerType()], NoType(), False)

        # Blocked because other_foo can't set a value for foo[1]
        self.assertFalse(foo.is_copyable_from(other_foo, {}))


class TestCompileTimeUnitTypeChecks(TestCase):
    def test_successful_basic_assignment(self):
        foo = IntegerType()
        self.assertTrue(foo.is_copyable_from(IntegerType(), {}))

    def test_successful_basic_assignment2(self):
        foo = IntegerType()
        self.assertTrue(foo.is_copyable_from(UnitType(5), {}))

    def test_failed_basic_assignment(self):
        foo = UnitType(5)
        self.assertFalse(foo.is_copyable_from(IntegerType(), {}))

    def test_failed_basic_assignment2(self):
        foo = UnitType(5)
        self.assertFalse(foo.is_copyable_from(UnitType(6), {}))

    def test_failed_basic_assignment3(self):
        foo = UnitType(5)
        self.assertTrue(foo.is_copyable_from(UnitType(5), {}))

    def test_successful_composite_assignment(self):
        foo = ObjectType({
            "foo": IntegerType()
        }, False)
        other_foo = ObjectType({
            "foo": UnitType(5)
        }, True)
        self.assertTrue(foo.is_copyable_from(other_foo, {}))

    def  test_successful_nested_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False)
        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": UnitType(5)
            }, True)
        }, False)
        self.assertTrue(foo.is_copyable_from(other_foo, {}))


class TestCompileTimeOneOfTypeChecks(TestCase):
    def test_unitary_one_of_type(self):
        self.assertTrue(
            are_bindable(
                merge_types([ IntegerType(), IntegerType() ]),
                IntegerType(),
                False, False, {}
            )
        )

    def test_merge_unit_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ UnitType(5), UnitType(5) ]),
                UnitType(5),
                False, False, {}
            )
        )

    def test_merge_unit_and_broader_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ UnitType(5), IntegerType() ]),
                IntegerType(),
                False, False, {}
            )
        )

    def test_merge_integer_and_broader_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ IntegerType(), AnyType() ]),
                AnyType(),
                False, False, {}
            )
        )

    def test_merge_different_unit_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ UnitType(5), UnitType(10), UnitType(15) ]),
                OneOfType([ UnitType(5), UnitType(10), UnitType(15) ]),
                False, False, {}
            )
        )

    def test_subsume_unit_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ UnitType(5), UnitType(10), UnitType(15), UnitType(20), IntegerType() ]),
                IntegerType(),
                False, False, {}
            )
        )

    def test_combine_identical_object_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": IntegerType() }, False), ObjectType({ "foo": IntegerType() }, False) ]),
                ObjectType({ "foo": IntegerType() }, False),
                False, False, {}
            )
        )

    def test_combine_different_property_object_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": IntegerType() }, False), ObjectType({ "bar": IntegerType() }, False) ]),
                OneOfType([ ObjectType({ "foo": IntegerType() }, False), ObjectType({ "bar": IntegerType() }, False) ]),
                False, False, {}
            )
        )

    def test_combine_different_property_types_object_types(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": IntegerType() }, False), ObjectType({ "foo": StringType() }, False) ]),
                OneOfType([ ObjectType({ "foo": IntegerType() }, False), ObjectType({ "foo": StringType() }, False) ]),
                False, False, {}
            )
        )

    def test_revconst_preserved(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": IntegerType() }, True) ]),
                ObjectType({ "foo": IntegerType() }, True),
                False, False, {}
            )
        )

    def test_single_revconst_is_dominated_by_nonrevconst(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": IntegerType() }, True), ObjectType({ "foo": IntegerType() }, False) ]),
                ObjectType({ "foo": IntegerType() }, False),
                False, False, {}
            )
        )

    def test_double_revconst_allows_merge(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": UnitType(5) }, True), ObjectType({ "foo": IntegerType() }, True) ]),
                ObjectType({ "foo": IntegerType() }, True),
                False, False, {}
            )
        )

    def test_double_incompatible_non_revconst_blocks_merge(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": AnyType() }, False), ObjectType({ "foo": IntegerType() }, False) ]),
                OneOfType([ ObjectType({ "foo": AnyType() }, False), ObjectType({ "foo": IntegerType() }, False) ]),
                False, False, {}
            )
        )

    def test_double_incompatible_revconst_blocks_merge2(self):
        self.assertTrue(
            are_bindable(
                merge_types([ ObjectType({ "foo": UnitType(5) }, True), ObjectType({ "foo": UnitType(6) }, True) ]),
                OneOfType([ ObjectType({ "foo": UnitType(5) }, True), ObjectType({ "foo": UnitType(6) }, True) ]),
                False, False, {}
            )
        )

class TestRuntimeObjectMutationChecks(TestCase):

    def test_successful_basic_assignment(self):
        foo = Object({
            "bar": 5
        })

        foo.bar = 10

    def test_successful_basic_assignment_with_different_type(self):
        foo = Object({
            "bar": 5
        })

        foo.bar = "hello"

    def test_successful_odd_assignment_with_different_type(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        foo.bar.baz = 10
        foo.bar = "hello"

    def test_successful_assignment_with_type_check(self):
        foo = Object({
            "bar": 5
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

        foo.bar = 6

    def test_rejected_assignment_with_different_type(self):
        foo = Object({
            "bar": 5
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

        with self.assertRaises(IncompatableAssignmentError):
            foo.bar = "hello"

    def test_successful_assignment_with_structural_type(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        foo.bar = Object({
            "baz": 42
        })


    def test_rejected_replacement_with_structural_type(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        replacement_bar = Object({
            "baz": "hello"
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        with self.assertRaises(IncompatableAssignmentError):
            foo.bar = replacement_bar

    def test_rejected_incompatible_constraints(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        replacement_bar = Object({
            "baz": 42
        })

        get_manager(replacement_bar).create_reference(ObjectType({
            "baz": AnyType()
        }, False), False)

        # Fails because the second reference on replacement_bar would allow
        # replacement_bar.baz = "hello" which would in turn invalidate the
        # first reference on foo.
        with self.assertRaises(IncompatableAssignmentError):
            foo.bar = replacement_bar

class TestRuntimeObjectTypeCastingChecks(TestCase):

    def test_successful_single_create_reference(self):
        foo = Object({
            "bar": 5
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_successful_single_create_reference_with_unused_properties(self):
        foo = Object({
            "bar": 5,
            "baz": True
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_successful_single_create_reference_with_broad_properties(self):
        foo = Object({
            "bar": 5
        })

        # This is an important test. No one else has a reference to this object. We can still grab it with bar being Any,
        # and we can modify it too. This is not possible in static or dynamic programming
        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)

    def test_failure_single_create_multiple_references_with_broad_but_different_properties(self):
        foo = Object({
            "bar": 5
        })

        # This fails on the second create_reference because the reference from the first call would allow
        # foo.bar = "how are you?"
        # and that would break on the second call
        # Integer baz = foo.bar
        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)
        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ObjectType({
                "bar": IntegerType()
            }, False), False)

    def test_success_single_create_multiple_references(self):
        foo = Object({
            "bar": 5
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)
        get_manager(foo).create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_failed_single_create_reference_with_extra_properties(self):
        foo = Object({
            "bar": 5,
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because we're asking the object to have a baz fields, which it doesn't
            get_manager(foo).create_reference(ObjectType({
                "bar": IntegerType(),
                "baz": BooleanType()
            }, False), False)

    def test_successful_single_create_nested_reference(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

    def test_failed_single_create_nested_reference_with_wrong_type(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because the reference we create would allow
            # foo.bar.baz = True
            get_manager(foo).create_reference(ObjectType({
                "bar": ObjectType({
                    "baz": BooleanType()
                }, False)
            }, False), False)

    def test_succeeded_single_create_nested_reference_with_broad_type(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        # Allowed because no one else has a reference to the object yet
        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, False)
        }, False), False)

    def test_succeeded_create_nested_any_reference(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        # Allowed because no one else has a reference to this object yet
        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)

    def test_failed_create_multiple_different_nested_references(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        # Allowed because no one else has a reference to this object yet
        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)

        with self.assertRaises(CreateReferenceError):
            # Fails because the previous reference could do foo.bar = "hello"
            get_manager(foo).create_reference(ObjectType({
                "bar": ObjectType({
                    "baz": IntegerType()
                }, False)
            }, False), False)

    def test_succeeded_create_multiple_different_nested_references_with_const(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }, False), False)

        # Allowed because the previous reference is broad but const
        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

    def test_successful_create_multiple_different_nested_references_in_reverse_order_with_const(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        get_manager(foo).create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        get_manager(foo).create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }, False), False)

class TestRuntimeListTypeCastingChecks(TestCase):
    def test_successful_empty_list_create_reference(self):
        foo = List([])

        get_manager(foo).create_reference(ListType([], IntegerType(), False), False)

    def test_successful_integer_list_create_reference(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], IntegerType(), False), False)

    def test_successful_integer_list_create_reference2(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], AnyType(), False), False)

    def test_successful_integer_list_create_reference3(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([ IntegerType() ], IntegerType(), False), False)

    def test_successful_integer_list_create_reference4(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([ AnyType() ], IntegerType(), False), False)

    def test_successful_integer_list_create_reference5(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([ AnyType(), AnyType(), AnyType() ], NoType(), False), False)

#     def test_failed_integer_list_create_reference(self):
#        No way at the moment to say "don't accept extra entry types"
#         foo = List([5, 3, 7])
# 
#         with self.assertRaises(CreateReferenceError):
#             get_manager(foo).create_reference(ListType([ AnyType() ], NoType(), False), False)

    def test_failed_integer_list_create_reference2(self):
        foo = List([5, 3, 7])

        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([ AnyType() ], StringType(), False), False)

    def test_failed_integer_list_create_reference3(self):
        foo = List([5, 3, 7])

        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([ StringType() ], AnyType(), False), False)

    def test_failed_multiple_list_create_reference1A(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], IntegerType(), False), False)
        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([], AnyType(), False), False)

    def test_failed_multiple_list_create_reference1B(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], AnyType(), False), False)
        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([], IntegerType(), False), False)

    def test_failed_multiple_list_create_reference2A(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([ IntegerType() ], AnyType(), False), False)
        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([], AnyType(), False), False)

    def test_failed_multiple_list_create_reference2B(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], AnyType(), False), False)
        with self.assertRaises(CreateReferenceError):
            get_manager(foo).create_reference(ListType([ IntegerType() ], AnyType(), False), False)


    def test_successful_multiple_list_create_reference1(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([], AnyType(), False), False)
        get_manager(foo).create_reference(ListType([], AnyType(), False), False)

    def test_successful_multiple_list_create_reference2(self):
        foo = List([5, 3, 7])

        get_manager(foo).create_reference(ListType([ IntegerType() ], AnyType(), False), False)
        get_manager(foo).create_reference(ListType([ IntegerType() ], AnyType(), False), False)

if __name__ == '__main__':
    unittest.main()
