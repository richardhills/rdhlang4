# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from unittest.case import TestCase
import unittest.main

from exception_types import CreateReferenceError
from type_system.core_types import IncompatableAssignmentError, merge_types, \
    OneOfType, ObjectType, IntegerType, BooleanType, AnyType, UnitType,\
    are_bindable
from type_system.values import Object


# Golden rules:
# At compile time, be conservative. Block anything that might allow me to break someone else, or might allow someone else to break me.
# At runtime, be liberal. Block only things that we know will either break us or something else, using the greater amount of information to hand.
#
# Modifiers, like const, allow more types of assignment, because the range of things that might break is reduced
class TestCompileTimeChecks(TestCase):
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

        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertTrue(foo.is_copyable_from(other_foo))

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

        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertFalse(are_bindable(foo, other_foo, False, False))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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

        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))

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
        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertFalse(foo.is_copyable_from(other_foo))


class TestCompileTimeUnitTypeChecks(TestCase):
    def test_successful_basic_assignment(self):
        foo = IntegerType()
        self.assertTrue(foo.is_copyable_from(IntegerType()))

    def test_successful_basic_assignment2(self):
        foo = IntegerType()
        self.assertTrue(foo.is_copyable_from(UnitType(5)))

    def test_failed_basic_assignment(self):
        foo = UnitType(5)
        self.assertFalse(foo.is_copyable_from(IntegerType()))

    def test_failed_basic_assignment2(self):
        foo = UnitType(5)
        self.assertFalse(foo.is_copyable_from(UnitType(6)))

    def test_failed_basic_assignment3(self):
        foo = UnitType(5)
        self.assertTrue(foo.is_copyable_from(UnitType(5)))

    def test_successful_composite_assignment(self):
        foo = ObjectType({
            "foo": IntegerType()
        }, False)
        other_foo = ObjectType({
            "foo": UnitType(5)
        }, True)
        self.assertTrue(foo.is_copyable_from(other_foo))

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
        self.assertTrue(foo.is_copyable_from(other_foo))


class TestCompileTimeOneOfTypeChecks(TestCase):
    def test_unitary_one_of_type(self):
        self.assertEquals(
            merge_types([ IntegerType(), IntegerType() ]),
            IntegerType()
        )

    def test_merge_unit_types(self):
        self.assertEquals(
            merge_types([ UnitType(5), UnitType(5) ]),
            UnitType(5)
        )

    def test_merge_unit_and_broader_types(self):
        self.assertEquals(
            merge_types([ UnitType(5), IntegerType() ]),
            IntegerType()
        )

    def test_merge_integer_and_broader_types(self):
        self.assertEquals(
            merge_types([ IntegerType(), AnyType() ]),
            AnyType()
        )

    def test_merge_different_unit_types(self):
        self.assertEquals(
            merge_types([ UnitType(5), UnitType(10), UnitType(15) ]),
            OneOfType([ UnitType(5), UnitType(10), UnitType(15) ])
        )

    def test_subsume_unit_types(self):
        self.assertEquals(
            merge_types([ UnitType(5), UnitType(10), UnitType(15), UnitType(20), IntegerType() ]),
            IntegerType()
        )


class TestRuntimeMutationChecks(TestCase):

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

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

        foo.bar = 6

    def test_rejected_assignment_with_different_type(self):
        foo = Object({
            "bar": 5
        })

        foo.create_reference(ObjectType({
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

        foo.create_reference(ObjectType({
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

        foo.create_reference(ObjectType({
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

        foo.create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        replacement_bar = Object({
            "baz": 42
        })

        replacement_bar.create_reference(ObjectType({
            "baz": AnyType()
        }, False), False)

        # Fails because the second reference on replacement_bar would allow
        # replacement_bar.baz = "hello" which would in turn invalidate the
        # first reference on foo.
        with self.assertRaises(IncompatableAssignmentError):
            foo.bar = replacement_bar

class TestRuntimeCastingChecks(TestCase):

    def test_successful_single_create_reference(self):
        foo = Object({
            "bar": 5
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_successful_single_create_reference_with_unused_properties(self):
        foo = Object({
            "bar": 5,
            "baz": True
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_successful_single_create_reference_with_broad_properties(self):
        foo = Object({
            "bar": 5
        })

        # This is an important test. No one else has a reference to this object. We can still grab it with bar being Any,
        # and we can modify it too. This is not possible in static or dynamic programming
        foo.create_reference(ObjectType({
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
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)
        with self.assertRaises(CreateReferenceError):
            foo.create_reference(ObjectType({
                "bar": IntegerType()
            }, False), False)

    def test_success_single_create_multiple_references(self):
        foo = Object({
            "bar": 5
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)
        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }, False), False)

    def test_failed_single_create_reference_with_extra_properties(self):
        foo = Object({
            "bar": 5,
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because we're asking the object to have a baz fields, which it doesn't
            foo.create_reference(ObjectType({
                "bar": IntegerType(),
                "baz": BooleanType()
            }, False), False)

    def test_successful_single_create_nested_reference(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        foo.create_reference(ObjectType({
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
            foo.create_reference(ObjectType({
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
        foo.create_reference(ObjectType({
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
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)

    def test_failed_create_multiple_different_nested_references(self):
        foo = Object({
            "bar": Object({
                "baz": 5
            })
        })

        # Allowed because no one else has a reference to this object yet
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }, False), False)

        with self.assertRaises(CreateReferenceError):
            # Fails because the previous reference could do foo.bar = "hello"
            foo.create_reference(ObjectType({
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

        foo.create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }, False), False)

        # Allowed because the previous reference is broad but const
        foo.create_reference(ObjectType({
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

        foo.create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, False)
        }, False), False)

        foo.create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }, False), False)


if __name__ == '__main__':
    unittest.main()
