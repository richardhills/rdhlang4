/** Taken from "The Definitive ANTLR 4 Reference" by Terence Parr */

// Derived from http://json.org
grammar lang;

code
   : literal EOF          # toLiteral
   | functionStub EOF     # toFunctionStub
   ;

functionStub
   : expression symbolInitialization (',' symbolInitialization)* ';' functionStub? # localVariableDeclaration
   | 'static' symbolInitialization ';' functionStub? # staticValueDeclaration
   | 'typedef' expression SYMBOL ';' functionStub? # typedef
   | 'import' SYMBOL ';' functionStub? # importStatement
   | (expression ';')+ functionStub? # toExpression
   ;

symbolInitialization
   : SYMBOL '=' expression
   ;

newObject
   : '{' pair (',' pair)* '}'
   | '{' '}'
   ;

pair
   : SYMBOL ':' expression
   | STRING ':' expression
   ;

literal
   : STRING
   | NUMBER
   | objectLiteral
   | functionLiteral
   ;

objectLiteral
   : '{' literalPair (',' literalPair)* '}'
   | '{' '}'
   ;

literalPair
   : SYMBOL ':' literal
   | STRING ':' literal
   ;
   
newTuple
   : '[' expression? (',' expression)* ']'
   ;

expression
   : expression '.' SYMBOL         # boundDereference
   | expression '[' expression ']' # dynamicDereference
   | SYMBOL                        # unboundDereference
   | expression '(' ')'            # noParameterFunctionInvocation
   | expression '(' expression ')' # singleParameterFunctionInvocation
   | '(' expression ')'            # parenthesis
   | '+' expression                # makePositive
   | '-' expression                # negation
   | expression '*' expression     # multiplication
   | expression '/' expression     # division
   | expression '+' expression     # addition
   | expression '-' expression     # subtraction
   | expression '%' expression     # modulus
   | expression '>=' expression    # gte
   | expression '<=' expression    # lte
   | expression '>' expression     # gt
   | expression '<' expression     # lt
   | expression '==' expression    # equals
   | expression '!=' expression    # notEquals
   | expression '=' expression     # assignment
   | STRING                        # string
   | NUMBER                        # number
   | whileLoop                     # toWhileLoop
   | ifBlock                       # toIf
   | functionLiteral               # toFunctionLiteral
   | newObject                     # toNewObject
   | newTuple                      # toNewTuple
   | 'true'                        # true
   | 'false'                       # false
   | 'null'                        # null
   | voidType                      # toVoidType
   | inferredType                  # toInferredType
   | integerType                   # toIntegerType
   | stringType                    # toStringType
   | functionType                  # toFunctionType
   | objectType                    # toObjectType
   | tupleType                     # toTupleType
   | listType                      # toListType
   | anyType                       # toAnyType
   | constTypeModifier             # toConstTypeModifier
   | returnExpression              # toReturnExpression
   | exitExpression                # toExitExpression
   ;

voidType
   : 'Void'
   ;

inferredType
   : 'var'
   ;

integerType
   : 'Integer'
   ;

stringType
   : 'String'
   ;

functionType
   : 'Function' '<' expression '=>' expression '>' functionExits?
   ;

objectType
   : 'Object' '{' (propertyType ';')* '}'
   ;

listType
   : 'List' '<' expression '>'
   ;

tupleType
   : 'Tuple' '<' expression (',' expression)* '>'
   ;

anyType
   : 'Any'
   ;

constTypeModifier
   : 'const' expression
   ;

propertyType
   : expression SYMBOL
   ;

whileLoop
   : 'while' '(' expression ')' '{' functionStub? '}'
   ;

ifBlock
   : 'if' '(' expression ')' '{' functionStub? '}' ('else' '{' functionStub? '}')?
   ;

functionLiteral
   : 'function' functionArgumentAndReturns functionThrows? functionExits? '{' functionStub? '}'
   ;

functionArgumentAndReturns
   : '(' ')'
   | '(' expression ')'
   | '(' expression '=>' expression ')'
   ;

functionThrows
   : 'nothrow'
   | 'throws' expression
   ;

functionExits
   : 'noexit'
   ;

returnExpression
   : 'return' expression
   ;

exitExpression
   : 'exit' expression
   ;

SYMBOL
   : [a-zA-Z_] [a-zA-Z0-9_]*
   ;

STRING
   : '"' (ESC | SAFECODEPOINT)* '"'
   ;

fragment ESC
   : '\\' (["\\/bfnrt] | UNICODE)
   ;
fragment UNICODE
   : 'u' HEX HEX HEX HEX
   ;
fragment HEX
   : [0-9a-fA-F]
   ;
fragment SAFECODEPOINT
   : ~ ["\\\u0000-\u001F]
   ;


NUMBER
   : INT ('.' [0-9] +)? EXP?
   ;


fragment INT
   : '0' | [1-9] [0-9]*
   ;

// no leading zeros

fragment EXP
   : [Ee] [+\-]? INT
   ;

// \- since - means "range" inside [...]

WS
   : [ \t\n\r] + -> channel(HIDDEN)
   ;
