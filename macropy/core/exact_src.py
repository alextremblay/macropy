# -*- coding: utf-8 -*-
"""Logic related to lazily performing the computation necessary to finding
the source extent of an AST.

Exposed to each macro as an `exact_src` function."""

import ast

from . import unparse
from .macros import injected_vars
from .util import Lazy, distinct, register
from .walkers import Walker


# TODO: unused, but covers cases, which latest `exact_src` probably doesn't. Check, update, or move information to other place and delete.
@Walker
def indexer(tree, collect, **kw):
    try:
        # print('Indexer: %s' % ast.dump(tree), file=sys.stderr)
        unparse(tree)
        collect((tree.lineno, tree.col_offset))
    except (AttributeError, KeyError) as e:
        # If this handler gets executed it's because unparse() has
        # failed (it's being used as a poor man's syntax
        # checker). It's important to remember that unparse cannot
        # unparse *any* tree fragment. There are certain fragments,
        # (like an ast.Add without its parent ast.BinOp) that cannot
        # be unparsed alone
        pass
        # print("Failure in exact_src.py", e, file=sys.stderr)
        # raise


# FIXME: unused, probably time to delete.
_transforms = {
    ast.GeneratorExp: "(%s)",
    ast.ListComp: "[%s]",
    ast.SetComp: "{%s}",
    ast.DictComp: "{%s}"
}


@register(injected_vars)
def exact_src(tree, src, **kw):

    def exact_src_imp(tree, src):
        
        # Calculate indexies
        first_node, last_node = (tree[0], tree[-1]) if isinstance(tree, list) else (tree, tree)

        start_line = first_node.lineno-1
        last_line = last_node.end_lineno
        start_col = first_node.col_offset
        end_col = last_node.end_col_offset

        chunk_lines = src.split('\n')[start_line:last_line]
        if len(chunk_lines) > 1: # Multiline
            # From last line of code get chunk of code before end_col_offset
            last_str = chunk_lines.pop()[:end_col+1]
            # And return this line back to code lines array
            chunk_lines.append(last_str)
            # formate chunk by offset of first line and constract chunk into a single string
            prelim = '\n'.join([_line.replace(' ' * start_col, '') for _line in chunk_lines])

        elif len(chunk_lines) == 1: # Singleline
            prelim = chunk_lines[0][start_col:end_col]

        if isinstance(tree, ast.expr):
            x = "(" + prelim + ")"
        else:
            x = prelim

        try:
            parsed = ast.parse(x)
            if unparse(parsed).strip() == unparse(tree).strip():
                return prelim
        except SyntaxError as e:
            pass
        raise ExactSrcException(prelim)

    return lambda t: exact_src_imp(t, src)


class ExactSrcException(Exception):
    pass
