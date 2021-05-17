"""- Module    : app.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module communicates with the backend solver to solve minimum feedback arc set problems

You'll notice that we thread the solver instance and cache through several
functions. This is purposeful to get as close as possible to referential
transparency in python. Think of it as a Reader Monad carrying the cache and
solver handle.

"""

from pprint import pprint
import z3       as z
import networkx as nx
from   networkx import Graph

import matplotlib.pyplot as plt

import gadgets as g
import graphs  as gs
import utils   as u


def find_cycle(cache,s,graph):
    """Find a cycle in a graph. s is a solver object, graph is an adjacency list
    e.g. {0:[0,1,2,3,4,5], 1:[2,3] ...}. Given the graph iterate over the
    graph, convert the key and values to symbolic terms and check for a cycle.
    Returns the unsat core as a list of strings e.g. [1->2, 2->3, 3->4, 4->1]
    """
    for source, sinks in graph.adj.items():
        for sink in sinks:
            ## convert to strings
            s_source = str(source)
            s_sink   = str(sink)

            ## create symbolics
            sym_from = u.make_sym(cache,source)
            sym_to   = u.make_sym(cache,sink)

            ## lets go, this is just a fold over the dict yielding ()
            g.cycle_check(s, sym_from, sym_to, u.make_name(s_source,s_sink))

    r = []
    if s.check() == z.unsat: r = s.unsat_core()
    return u.parse_core(r)

def relax(graph, unsat_core, strategy):
    """Take a graph, an unsat-core and a strategy. use the strategy to find the
    edge to relax, relatx the edge and return the graph

    This function mutates graph
    """
    source, sink = strategy(unsat_core)
    graph.remove_edge(source, sink)

def go (cache,s,graph):
    # flag to end loop
    done = False

    # kick off
    while not done:
        # nx.draw(graph)
        # plt.show()

        # get the core
        core = find_cycle(cache, s, graph)
        pprint(core)
        pprint(graph.adj.items())

        # if the core is empty then we are done, if not then relax and recur
        if core:
            # relax an edge by some strategy
            relax(graph,core,lambda x : x[0])

            # this is good enough for now but in the future we should try to
            # remove only the right constraint, which will be much much faster
            s.reset()
        else:
            done = True


def main():
    # just use a heterogeneous map as a cache
    cache = {}

    # spin up the solver
    s = z.Solver()

    go(cache,s,gs.round_robin_graph)
