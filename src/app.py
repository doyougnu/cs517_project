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
import igraph   as ig

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
    for source, sink in graph.get_edgelist():
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
    # pprint([source, sink])
    # pprint(list(graph.adj.items()))
    # print("Before: ", nx.to_dict_of_lists(graph))
    graph.delete_edge(int(source),int(sink))
    # print("After: ", nx.to_dict_of_lists(graph))

    return graph

def runWithGraph(cache,s,graph):
    # flag to end loop
    done = False

    # kick off
    while not done:
        # nx.draw(graph)
        # plt.show()

        # get the core
        core = find_cycle(cache, s, graph)

        # if the core is empty then we are done, if not then relax and recur
        # print("Core: ", core)
        if core:
            # relax an edge by some strategy
            graph = relax(graph, core, lambda x : x[0])

            # this is good enough for now but in the future we should try to
            # remove only the right constraint, which will be much much faster
            s.reset()
        else:
            done = True

        # print("going: ", done)
        # print("graph Nodes: ", graph.nodes())
        # print("graph Edges: ", graph.edges())

    return graph

def run():
    cache = {}

    # spin up the solver
    s = z.Solver()

    g = ig.Graph.Erdos_Renyi(n=15,p=0.2)
    newG = runWithGraph(cache,s,g)
    print(newG.is_dag())
    return newG
