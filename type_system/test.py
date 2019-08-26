# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.case import TestCase
import unittest.main

from core_types import ObjectType, IntegerType, BooleanType, AnyType, Object, \
    Cell, CreateReferenceError, DataIntegrityError

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
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        })

        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_failed_with_different_types_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        })

        # This fails because it would allow me to do:
        # foo.baz = True
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_failed_covariant_with_different_types_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": AnyType()
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        })

        # This fails because it would allow me to do:
        # foo.baz = "hello, how are you"
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_successful_covariant_with_different_types_and_const_simple_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": AnyType(is_const=True)
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": IntegerType()
        })

        # Like the previous case, but with foo.baz explicitely blocked by const
        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_successful_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType(),
            "bam": IntegerType()
        })

        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_failed_contraviant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType(),
            "bam": IntegerType()
        })

        other_foo = ObjectType({
            "bar": IntegerType(),
            "baz": BooleanType()
        })

        # This fails because it would allow me to do:
        # foo.bam - which is undefined
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_successful_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_failed_with_different_types_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": BooleanType()
            })
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # This fails because it would allow me to do:
        # foo.bar.baz = True
        # OR
        # foo.bar = { baz: True }
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_failed_covariant_with_different_types_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            })
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # This fails because it would allow me to do:
        # foo.bar.baz = "hello, how are you?"
        # OR
        # foo.bar = { baz: "wazup?" }
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_failed_covariant_with_different_types_and_partial_const1_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, is_const=True)
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # This fails because it would allow me to do:
        # foo.bar.baz = "hello, how are you?"
        # ... although this is blocked:
        # foo.bar = { baz: "wazup?" }
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_failed_covariant_with_different_types_and_partial_const2_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType()
            }, is_const=True)
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # This fails because it would allow me to do:
        # foo.bar = { baz: "wazup?" }
        # ... but this would be blocked...
        # foo.bar.baz = "hello, how are you?"
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_successful_covariant_with_different_types_and_const_nesting_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": AnyType(is_const=True)
            }, is_const=True)
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # Like the previous 3 cases, but the 2 error cases are both blocked explicitely by the const
        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_failed_nesting_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            })
        })

        # This fails because it would allow me to do
        # foo.bar = { "baz": 123 }
        self.assertFalse(foo.is_initializable_from(other_foo))

    def test_succeeded_nesting_covariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            }, is_const=True)
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            })
        })

        # Like the previous case, but with foo.bar = ... blocked by the const
        self.assertTrue(foo.is_initializable_from(other_foo))

    def test_failed_nesting_contravariant_with_extra_fields_compile_time_object_assignment(self):
        foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType(),
                "bam": BooleanType()
            })
        })

        other_foo = ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        })

        # This fails because it would allow me to do
        # foo.bar.bam - which is undefined
        self.assertFalse(foo.is_initializable_from(other_foo))

class TestRuntimeChecks(TestCase):
    def test_basic_cell_creation1(self):
        with self.assertRaises(DataIntegrityError):
            # Fails because... y'know...
            Cell(1, BooleanType())

    def test_basic_cell_creation2(self):
        with self.assertRaises(DataIntegrityError):
            # Fails because the resulting cell would reference an object containing an integer, instead of an boolean.
            Cell(Object({ "foo": Cell(5, IntegerType()) }), ObjectType({ "foo": BooleanType() }))

    def test_successful_single_create_reference(self):
        foo = Object({
            "bar": Cell(5, IntegerType())
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }))

    def test_successful_single_create_reference_with_unused_properties(self):
        foo = Object({
            "bar": Cell(5, IntegerType()),
            "baz": Cell(True, BooleanType())
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }))

    def test_successful_single_create_reference_with_broad_properties(self):
        foo = Object({
            "bar": Cell(5, IntegerType())
        })

        # This is an important test. No one else has a reference to this object. We can still grab it with bar being Any,
        # and we can modify it too. This is not possible in static or dynamic programming
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }))

    def test_failure_single_create_multiple_references_with_broad_but_different_properties(self):
        foo = Object({
            "bar": Cell(5, IntegerType())
        })

        # This fails on the second create_reference because the reference from the first call would allow
        # foo.bar = "how are you?"
        # and that would break on the second call
        # Integer baz = foo.bar
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }))
        with self.assertRaises(CreateReferenceError):
            foo.create_reference(ObjectType({
                "bar": IntegerType()
            }))

    def test_success_single_create_multiple_references(self):
        foo = Object({
            "bar": Cell(5, IntegerType())
        })

        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }))
        foo.create_reference(ObjectType({
            "bar": IntegerType()
        }))

    def test_failed_single_create_reference_with_extra_properties(self):
        foo = Object({
            "bar": Cell(5, IntegerType()),
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because we're asking the object to have a baz fields, which it doesn't
            foo.create_reference(ObjectType({
                "bar": IntegerType(),
                "baz": BooleanType()
            }))

    def test_successful_single_create_nested_reference(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        foo.create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        }))

    def test_failed_single_create_nested_reference_with_wrong_type(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because the reference we create would allow
            # foo.bar.baz = True
            foo.create_reference(ObjectType({
                "bar": ObjectType({
                    "baz": BooleanType()
                })
            }))

    def test_failed_single_create_nested_reference_with_broad_type(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        with self.assertRaises(CreateReferenceError):
            # Fails because the reference we create would allow
            # foo.bar.baz = "how are you doing?"
            foo.create_reference(ObjectType({
                "bar": ObjectType({
                    "baz": AnyType()
                })
            }))

    def test_succeeded_create_nested_any_reference(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        # Allowed because no one else has a reference to this object yet
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }))

    def test_failed_create_multiple_different_nested_references(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        # Allowed because no one else has a reference to this object yet
        foo.create_reference(ObjectType({
            "bar": AnyType()
        }))

        with self.assertRaises(CreateReferenceError):
            # Fails because the previous reference could do foo.bar = "hello"
            foo.create_reference(ObjectType({
                "bar": ObjectType({
                    "baz": IntegerType()
                })
            }))


    def test_succeeded_create_multiple_different_nested_references_with_const(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        foo.create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }))

        foo.create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        }))

    def test_successful_create_multiple_different_nested_references_in_reverse_order_with_const(self):
        foo = Object({
            "bar": Cell(Object({
                "baz": Cell(5, IntegerType())
            }), ObjectType({
                "baz": IntegerType()
            }))
        })

        foo.create_reference(ObjectType({
            "bar": ObjectType({
                "baz": IntegerType()
            })
        }))

        foo.create_reference(ObjectType({
            "bar": AnyType(is_const=True)
        }))

if __name__ == '__main__':
    unittest.main()
