"""
- Module    : app.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module communicates with the backend solver to solve minimum feedback arc set problems
"""

from pprint import pprint
from z3     import *

import gadgets as g
import utils   as u


def find_cycle(s,graph):
    """Find a cycle in a graph. s is a solver object, graph is an adjacency list
    e.g. {0:[0,1,2,3,4,5], 1:[2,3] ...}. Given the graph iterate over the
    graph, convert the key and values to symbolic terms and check for a cycle.
    Returns the unsat core as a list of strings e.g. [1->2, 2->3, 3->4, 4->1]
    """
    for source, sinks in graph.items():
        for sink in sinks:
            ## convert to strings
            s_source = str(source)
            s_sink   = str(sink)

            ## create symbolics
            sym_from = Int(source)
            sym_to   = Int(sink)

            ## lets go, this is just a fold over the dict yielding ()
            g.cycle_check(s, sym_from, sym_to, u.make_name(s_source,s_sink))

    r = []
    if s.check() == unsat: r = s.unsat_core()
    return u.parse_core(r)

def relax(graph, unsat_core, strategy):


# s = Solver()
# cycle = find_cycle(s,round_robin_graph)
# pprint(cycle)
