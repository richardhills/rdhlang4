RDHLang4

Core principles:
1. Internal AST is JSON
2. Language is a superset of JSON
3. 2 stages: verification and execution
4. Verification stage consists of:
   a) Parsing input file into JSON
   b) Executing statics and storing result
   c) Verifying code
   d) On finding a prepare() call, executing parameter and repeating the verification process from b)
5. RTTI
6. Structural typing
7. Single Break flow control primitive

Type System
Values (objects, integers, strings etc) have run time types
Expressions (dereferences, etc) have static types and run time types

Primitive Types:
Number
String
Boolean

Algebraic Types:
Value<value>
Object<property_name: Type, ...>
Dict<KeyType: ValueType>
Tuple<ElementType, ...>
List<ElementType>
OneOf<Type1, ...>

Value Types:
Number
String
Boolean
Value<value>
Oneof<Type1, ...>
