#
# simpleArith.py
#
# Example of defining an arithmetic expression parser using
# the infixNotation helper method in pyparsing.
#
# Copyright 2006, by Paul McGuire
#
import sys
import pyparsing as pp
#from pyparsing import *

ppc = pp.pyparsing_common

pp.ParserElement.enablePackrat()
sys.setrecursionlimit(3000)

integer = ppc.integer
variable = pp.Word(pp.alphas, exact=1)
operand = integer | variable

expop = pp.Literal("^")
signop = pp.oneOf("+ -")
multop = pp.oneOf("* /")
plusop = pp.oneOf("+ -")
factop = pp.Literal("!")

# To use the infixNotation helper:
#   1.  Define the "atom" operand term of the grammar.
#       For this simple grammar, the smallest operand is either
#       and integer or a variable.  This will be the first argument
#       to the infixNotation method.
#   2.  Define a list of tuples for each level of operator
#       precedence.  Each tuple is of the form
#       (opExpr, numTerms, rightLeftAssoc, parseAction), where
#       - opExpr is the pyparsing expression for the operator;
#          may also be a string, which will be converted to a Literal
#       - numTerms is the number of terms for this operator (must
#          be 1 or 2)
#       - rightLeftAssoc is the indicator whether the operator is
#          right or left associative, using the pyparsing-defined
#          constants opAssoc.RIGHT and opAssoc.LEFT.
#       - parseAction is the parse action to be associated with
#          expressions matching this operator expression (the
#          parse action tuple member may be omitted)
#   3.  Call infixNotation passing the operand expression and
#       the operator precedence list, and save the returned value
#       as the generated pyparsing expression.  You can then use
#       this expression to parse input strings, or incorporate it
#       into a larger, more complex grammar.
#
expr = pp.infixNotation(
    operand,
    [
        ("!", 1, pp.opAssoc.LEFT),
        ("^", 2, pp.opAssoc.RIGHT),
        (signop, 1, pp.opAssoc.RIGHT),
        (multop, 2, pp.opAssoc.LEFT),
        (plusop, 2, pp.opAssoc.LEFT),
    ],
)

test = [
    "9 + 2 + 3",
    "9 + 2 * 3",
    "(9 + 2) * 3",
    "(9 + -2) * 3",
    "(9 + -2) * 3^2^2",
    "(9! + -2) * 3^2^2",
    "M*X + B",
    "M*(X + B)",
    "1+2*-3^4*5+-+-6",
    "(a + b)",
    "((a + b))",
    "(((a + b)))",
    "((((a + b))))",
    "((((((((((((((a + b))))))))))))))",
]
for t in test:
    print(t)
    print(expr.parseString(t))
    print("")