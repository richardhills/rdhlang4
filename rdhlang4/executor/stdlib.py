from rdhlang4.parser.rdhparser import prepare_code
from rdhlang4.parser.visitor import type_op
from rdhlang4.type_system.values import Object


add_function = prepare_code("""
    function(Any) {
        return dynamic function(Tuple<List<outer.argument>, outer.argument>) noexit {
            exec({
                "opcode": "splice",
                "list": {
                    "opcode": "dereference",
                    "reference": { "opcode": "literal", "value": 0 },
                    "of": {
                        "opcode": "dereference",
                        "reference": { "opcode": "literal", "value": "argument" },
                        "of": { "opcode": "context" }
                    }
                },
                "end": { "opcode": "literal", "value": 0 },
                "delete": { "opcode": "literal", "value": 0 },
                "insert": {
                    "opcode": "new_tuple",
                    "values": [{
                        "opcode": "dereference",
                        "reference": { "opcode": "literal", "value": 1 },
                        "of": {
                            "opcode": "dereference",
                            "reference": { "opcode": "literal", "value": "argument" },
                            "of": { "opcode": "context" }
                        }
                    }]
                }
            });
            return;
        };
    }
""", check_application_break_mode_constraints=False, include_stdlib=False)

STDLIB = Object({
    "add": add_function,
    "int": { "type": "Integer" },
    "string": { "type": "String" },
    "bool": { "type": "bool" },
    "any": { "type": "Any" }
})

