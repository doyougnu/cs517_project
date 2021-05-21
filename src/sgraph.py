"""- Module    : symgraph.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module that defines a symbolic graph. A symbolic graph is a graph of sat/smt
solver symbolic variables

"""

from z3 import *

class SGraph:

    def __init__(self):
        self._s_edges    = {}
        self._s_nodes    = {}
        self._s_adj_list = {}

    def s_nodes(self):
        return self._s_nodes

    def s_edges(self):
        return self._s_edges

    def s_adj_list(self):
        return list(self._s_adj_list.items())

    ## look at this repition....I hate it
    def make_sym_node(self,new,ty=Int):
        if new not in self._s_nodes:
            sym_new = ty(str(new))
            self._s_nodes[new] = sym_new
        return self._s_nodes[new]

    def make_sym_edge(self,new,ty=Int):
        if new not in self._s_edges:
            sym_new = ty(str(new))
            self._s_edges[new] = sym_new
        return self._s_edges[new]


    def add_adjacency(self,sym_source,sym_sink):
        if sym_source not in self._s_adj_list:
            self._s_adj_list[sym_source] = [sym_sink]
        else:
            self._s_adj_list[sym_source].append(sym_sink)

    def has_nodes(self):
        ## empty dicts are falsy
        return bool(self._s_nodes)

    def has_edges(self):
        ## empty dicts are falsy
        return bool(self._s_edges)

    def has_adj_list(self):
        ## empty dicts are falsy
        return bool(self._s_adj_list)
