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
import networkx as nx
from numpy import empty
from re import split

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

def flatten(list_o_lists):
    return [e for sublist in list_o_lists for e in sublist]


def find_all_cycles(graph):
    nx_graph = graph.to_networkx()
    return list(nx.simple_cycles(nx_graph))


def pairs(ls, n = 1):
    return list(zip(ls, ls[n:] + ls[:n]))


def mk_cycle_matrix(cycle_edge_list, num_edges):
    ps          = [pairs(edges) for edges in cycle_edge_list]
    cycle_count = len(cycle_edge_list)
    matrix      = [{}] * cycle_count
    for i in range(cycle_count):
        for pair in ps[i]:
            matrix[i][pair] = 1

    return matrix



# [[0, 1, 3, 4, 5, 2], [0, 1, 2], [3, 4, 5]]
# 0->1, 1->3, 3->4, 4->5, 5->2, 2->0
# matrix is i X Edges in graph
