from rdhlang4.parser.rdhparser import prepare_code

add_function = prepare_code("""
    function(Any) {
        return dynamic function(Tuple<List<outer.argument>, outer.argument>) nothrow noexit {
            argument[0][0] = argument[1];
            return;
        };
    }
""", check_application_break_mode_constraints=False)
