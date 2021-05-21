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

from pprint     import pprint
from functools  import reduce
import z3       as z
import igraph   as ig

import matplotlib.pyplot as plt

import gadgets as g
import graphs  as gs
import utils   as u
import sgraph  as sg

def symbolize_graph(sgraph,s,graph):
    """Given a variable cache, a solver object and an igraph graph. Translate every
    edge to a symbolic variable in the solver and return a new cache mapping
    names to symbolics

    """

    ## the cache will only be populated once because symbolic edges will be
    ## relaxes in the solver not in the python layer
    pprint(sgraph.s_nodes)

    if not sgraph.has_nodes():
        for source, sink in graph.get_edgelist():
            ## convert to strings
            s_source = str(source)
            s_sink   = str(sink)
            s_edge   = u.make_name(s_source,s_sink)

            ## create symbolics
            sym_source = sgraph.make_sym_node(s_source)
            sym_sink   = sgraph.make_sym_node(s_sink)
            sym_edge   = sgraph.make_sym_edge(s_edge)

            ## pack the symbolic adjacency list
            sgraph.add_adjacency(sym_source,sym_sink)

    return sgraph



def find_all_cycles(sgraph,s,graph):
    """Find a cycle in a graph. s is a solver object, graph is an igraph object.
    Given the graph iterate over the graph, convert the key and values to
    symbolic terms and check for a cycle. Returns the unsat core as a list of
    strings e.g. [1->2, 2->3, 3->4, 4->1]
    """

    ## get the symbolics
    sgraph = symbolize_graph(sgraph,s,graph)

    print(sgraph)

    ## enter new assertion level
    s.push()
    ## we have to use all edges or else this is violated
    # s.add(z.Product(list(u.cache_edges(cache).)) > 0)
    ## We cannot have cycles
    g.cycle_check(s,sgraph)

    r = []
    print(s.check())
    if s.check() == z.unsat:
        r = s.unsat_core()

    s.pop()

    return r


def runWithGraph(sgraph,s,graph):
    # flag to end loop
    done = False

    # kick off
    while not done:

        # get the core
        cores = find_all_cycles(sgraph, s, graph)

        # if the core is empty then we are done, if not then relax and recur
        print("Core: ", cores)

        done = True
        # if core:
        #     # relax an edge by some strategy
        #     graph = relax(graph, core, lambda x : x[0])

        #     # this is good enough for now but in the future we should try to
        #     # remove only the right constraint, which will be much much faster
        #     s.reset()
        # else:
        #     done = True

        # print("going: ", done)
        # print("graph Nodes: ", graph.nodes())
        # print("graph Edges: ", graph.edges())

    return graph

def run():
    sgraph = sg.SGraph()

    # spin up the solver
    s = z.Solver()

    g = gs.round_robin_graph
    newG = runWithGraph(sgraph,s,g)
    print(newG.is_dag())
    return u.edge_to_list_dict(newG)
