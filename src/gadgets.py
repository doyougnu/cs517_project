"""
- Module    : Gadgets.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines gadgets for minimum feedback arc set encoding to SAT
"""

import functools
from pprint import pprint
from z3 import *


round_robin_graph = { 0: [1,2,3,4,5],
                      1: [2,3,5],
                      2: [3,4],
                      3: [4,5],
                      4: [1],
                      5: [2,4]
                    }

anti_greed_graph = { 0: [1],
                     1: [2,3],
                     2: [0],
                     3: [4],
                     4: [5],
                     5: [3,2]
                   }

def make_name(frm,to): return frm + "->" + to

def cycle_check(s,v_from,v_to,name):
    """The cycle check is extremely simple, number the vertices in the graph from 0
    to n, then for each edge from v_from to v_to create a constraint that
    v_from < v_to. This encoding simply counts the edges that are traversed
    (and is similar to deBruijn indices actually!) so a cycle is the occurrence
    of a vertex from an Int i to an Int j where i < j.
    """
    # edge_constraint
    s.assert_and_track(v_from < v_to, name)


def find_cycle(s,graph):
    for source, sinks in graph.items():
        for sink in sinks:
            ## convert to strings
            s_source = str(source)
            s_sink   = str(sink)

            ## create symbolics
            sym_from = Int(source)
            sym_to   = Int(sink)

            ## lets go, this is just a fold over the dict yielding ()
            cycle_check(s, sym_from, sym_to, make_name(s_source,s_sink))

    r = []
    if s.check() == unsat: r = s.unsat_core()
    return r


s = Solver()
cycle = find_cycle(s,round_robin_graph)
pprint(cycle)
