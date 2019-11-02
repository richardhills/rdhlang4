# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from executor.executor import PreparedFunction
from parser.rdhparser import parse
from parser.visitor import function_literal, object_type, new_object_op, \
    transform_op, prepare_op, decompose_function, assignment_op, \
    symbolic_dereference_ops, type, literal_op


def main():
    executor = function_literal(
        type("Void"),
        new_object_op({}),
        {},
        object_type({}),
        new_object_op({}), [
            assignment_op(
                symbolic_dereference_ops(["local"]),
                literal_op(decompose_function(
                    type("Void"),
                    new_object_op({}),
                    {},
                    {},
                    new_object_op({}),
                    [
                        prepare_op(symbolic_dereference_ops(["argument"])),
                        transform_op(symbolic_dereference_ops(["local"]), output="return")
                    ]
                ))
            )
        ]
    )

    executor = PreparedFunction(executor)
    while True:
        code = raw_input(">")
        ast = parse(code)
        executor.invoke(ast)

if __name__ == '__main__':
    main()
