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
import utils as u
import sgraph as sg

def cycle_check(s,sgraph):
    """The cycle check is extremely simple, number the vertices in the graph from 0
    to n, then for each edge from v_from to v_to create a constraint that
    v_from < v_to. This encoding simply counts the edges that are traversed
    (and is similar to deBruijn indices actually!) so a cycle is the occurrence
    of a vertex from an Int i to an Int j where i < j. We add an extra
    constraint that the edge is not indicated by a 0. In the solver a 0 on an
    edge means the edge has been relaxed in the symbolic graph

    """

    print(sgraph.s_adj_list())

    for sym_source, sinks in sgraph.s_adj_list():
        for sym_sink in sinks:
            # # edge_constraint
            edge_name = u.make_name(str(sym_source), str(sym_sink))
            s.assert_and_track(sym_source < sym_sink, edge_name)
