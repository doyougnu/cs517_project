"""
- Module    : utils.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Common utility functions
"""

from z3 import *

def make_name(frm,to): return frm + "->" + to

def parse_edge(edge): # return list(map(int,edge.__str__().split("->")))
    str_edge = edge.__str__()
    return list(map(lambda x: x,str_edge.split("->")))

def parse_core(core):
    """Parse an unsat core. An unsat core is shallowly embedded as a list of z3
    BoolRef objects such as: [1->2, 2->3, 3->4, 4->1], to operate on these we
    need to coerce them to a string parse the string and coerce the Ints out.

    Input:  List of strings, e.g.,      [1->2  , 2->3  , 3->4  , 4->1  ]
    Output: List of List of Ints, e.g., [[1, 2], [2, 3], [3, 4], [4, 1]]

    """
    return list(map(lambda e: parse_edge(e), core))

def make_sym(cache, new, ty=Int):
    """Create a new symbolic variable in the backend solver. We use a cache to
    avoid repeated calls to the solver. Furthermore, because we are naming
    constraints we must ensure that we don't accidental use a duplicate name in
    the solver or else it will throw an exception
    """

    if new not in cache:
        sym_new = ty(str(new))
        cache[new] = sym_new

    return cache, cache[new]

def edge_to_list_dict(g):
    """ Convert a graph to a dictionary of edges
    """
    ret = {}
    for source,sink in g.get_edgelist():
        if source not in ret.keys():
            ret[source] = []

        ret[source].append(sink)

    return ret

def remove_edge(g,source,sink):
    """Given an igraph graph, a source vertex and a sink vertex remove the edge
    connecting the source and the sink from the igraph graph. This function
    mutates g.
    """
    g.delete_edges(g.get_eid(source,sink))
