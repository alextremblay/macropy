import ast

import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.expr
def g(tree, **kw):
    return ast.Constant(value = 0)

@macros.expr
def f(tree, **kw):
    return ast.Constant(value = 0)
