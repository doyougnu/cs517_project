"""
- Module    : gadgets.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines gadgets for minimum feedback arc set encoding to SAT
"""

from z3 import *

def cycle_check(s,v_from,v_to,name):
    """The cycle check is extremely simple, number the vertices in the graph from 0
    to n, then for each edge from v_from to v_to create a constraint that
    v_from < v_to. This encoding simply counts the edges that are traversed
    (and is similar to deBruijn indices actually!) so a cycle is the occurrence
    of a vertex from an Int i to an Int j where i < j.
    """
    # edge_constraint
    s.assert_and_track(v_from < v_to, name)
