/** Taken from "The Definitive ANTLR 4 Reference" by Terence Parr */

// Derived from http://json.org
grammar lang;

code
   : literal
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
   
array
   : '[' expression (',' expression)* ']'
   | '[' ']'
   ;

expression
   : expression '.' SYMBOL         # boundDereference
   | SYMBOL                        # unboundDereference
   | expression '(' ')'            # noParameterFunctionInvocation
   | expression '(' expression ')' # singleParameterFunctionInvocation
   | expression '*' expression     # multiplication
   | expression '+' expression     # addition
   | expression '=' expression     # assignment
   | STRING                        # string
   | NUMBER                        # number
   | functionLiteral               # toFunctionLiteral
   | newObject                     # toNewObject
   | array                         # toArray
   | 'true'                        # true
   | 'false'                       # false
   | 'null'                        # null
   | voidType                      # toVoidType
   | inferredType                  # toInferredType
   | integerType                   # toIntegerType
   | stringType                    # toStringType
   | functionType                  # toFunctionType
   | objectType                    # toObjectType
   | anyType                       # toAnyType
   | returnExpression              # toReturnExpression
   ;

statement
   : expression SYMBOL '=' expression # localVariableDeclaration
   | 'static' SYMBOL '=' expression # staticValueDeclaration
   | 'typedef' expression SYMBOL # typedef
   | expression # toExpression
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
   : 'Function' '<' expression '=>' expression '>'
   ;

objectType
   : 'Object' '{' (propertyType ';')* '}'
   ;

anyType
   : 'Any'
   ;

propertyType
   : expression SYMBOL
   ;

functionLiteral
   : 'function' functionArgumentAndReturns functionThrows? '{' (statement ';')* '}'
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

returnExpression
   : 'return' expression
   ;

SYMBOL
   : [a-zA-Z] [a-zA-Z0-9]*
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
   : '-'? INT ('.' [0-9] +)? EXP?
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
