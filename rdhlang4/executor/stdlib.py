from rdhlang4.parser.rdhparser import prepare_code

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
                "start": { "opcode": "literal", "value": -1 },
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