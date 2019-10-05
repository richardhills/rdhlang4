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

otherExpressions
   : STRING
   | NUMBER
   | newObject
   | array
   | 'true'
   | 'false'
   | 'null'
   | voidType
   | integerType
   | stringType
   | functionType
   | assignment
   | returnExpression
   | dereference
   ;	

additionSubtractionAndOtherExpressions
   : additionSubtractionAndOtherExpressions '+' otherExpressions  # addition
   | otherExpressions # toOtherExpressions
   ;

expression
   : additionSubtractionAndOtherExpressions
   ;

statement
   : expression SYMBOL '=' expression # localVariableDeclaration
   | expression # toExpression
   ;

voidType
   : 'Void'
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

functionLiteral
   : functionLiteralWithTypes
   | functionLiteralWithoutTypes
   ;

functionLiteralWithTypes
   : 'function' '(' ( expression '=>' expression ) ')' '{' (statement ';')* '}'
   ;

functionLiteralWithoutTypes
   : 'function' '(' ')' '{' (statement ';')* '}'
   ;

assignment
   : dereference '=' expression
   ;

returnExpression
   : 'return' expression
   ;

dereference
   : SYMBOL (| expression '.' SYMBOL)
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
