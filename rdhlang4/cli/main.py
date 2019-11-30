# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
from sys import stdin

from rdhlang4.exception_types import PreparationException
from rdhlang4.executor.executor import PreparedFunction, BreakException
from rdhlang4.parser.rdhparser import parse


def main():
    parser = argparse.ArgumentParser(description='Validate and optionally run a script from stdin')
    parser.add_argument("--execute", help="Execute the input after validation", action="store_true")
    args = parser.parse_args()

    program = stdin.read()

    try:
        ast = parse(program)
        function = PreparedFunction(ast)
    except PreparationException as e:
        print "Error preparing function {}".format(e.args)
        return

    if not args.execute:
        print "Code can terminate by:"
        print function.break_types
        return

    try:
        function.jump()
    except BreakException as b:
        print "Code termination type {} with {}".format(b.mode, b.value)

if __name__ == "__main__":
    main()
