"""
- Module    : utils.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Common utility functions
"""

import z3 as z

def make_name(frm,to): return frm + "->" + to

def parse_edge(edge): return list(map(int,edge.split("->")))

def parse_core(core):
    """Parse an unsat core. An unsat core is shallowly embedded as a list of
    strings such as: ['1->2', '2->3', '3->4', '4->1'], to operate on these we
    need to parse the string and coerce the Ints out.

    Input:  List of strings, e.g.,      ['1->2', '2->3', '3->4', '4->1']
    Output: List of List of Ints, e.g., [[1, 2], [2, 3], [3, 4], [4, 1]]

    """
    return list(map(lambda e: parse_edge(e), core))

def make_sym(cache,new, ty = z.Int):
    """Create a new symbolic variable in the backend solver. We use a cache to
    avoid repeated calls to the solver. Furthermore, because we are naming
    constraints we must ensure that we don't accidental use a duplicate name in
    the solver or else it will throw an exception
    """

    if new not in cache:
        sym_new = ty(str(new))
        cache.insert(new,sym_new)

    return cache, cache[new]
