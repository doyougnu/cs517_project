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

def cycle_check(s,graph):
    """The cycle check is extremely simple, number the vertices in the graph from 0
    to n, then for each edge from v_from to v_to create a constraint that
    v_from < v_to. This encoding simply counts the edges that are traversed
    (and is similar to deBruijn indices actually!) so a cycle is the occurrence
    of a vertex from an Int i to an Int j where i < j. We add an extra
    constraint that the edge is not indicated by a 0. In the solver a 0 on an
    edge means the edge has been relaxed in the symbolic graph

    """


    node_cnt = len(graph)
    k = Int("k")
    syms = [Int('node%s'%i) for i in range(node_cnt)]

    s.add(syms[0] == 0) # start node is a 0
    s.add(k < node_cnt)
    s.add(k > 1)

    # for source, sinks in sgraph.s_adj_list():
    for i in range(node_cnt):
        s.add(syms[i] > 0)
        s.add(Or([syms[j] == ((syms[i] + 1) % k) for j in graph[i]]))
        # for sym_sink in sinks:
        #     ## edge_constraint
        #     edge_name = u.make_name(str(sym_source), str(sym_sink))
        #     # s.assert_and_track(sym_source < sym_sink, edge_name)
        #     # s.add(XOr(sgraph.s_edges()[edge_name] > 0, sym_source < sym_sink))
        #     s.add(sym_source > sym_sink)
    # gr      = { 0: [1, 4, 5],
    #             1: [0, 7, 2],
    #             2: [1, 9, 3],
    #             3: [2, 11, 4],
    #             4: [3, 13, 0],
    #             5: [0, 14, 6],
    #             6: [5, 16, 7],
    #             7: [6, 8, 1],
    #             8: [7, 17, 9],
    #             9: [8, 10, 2],
    #             10: [9, 18, 11],
    #             11: [10, 3, 12],
    #             12: [11, 19, 13],
    #             13: [12, 14, 4],
    #             14: [13, 15, 5],
    #             15: [14, 16, 19],
    #             16: [6, 17, 15],
    #             17: [16, 8, 18],
    #             18: [10, 19, 17],
    #             19: [18, 12, 15] }

    # L = len(gr)
    # cv = [Int('cv%s'%i) for i in range(L)]
    # s.add(cv[0]==0)
    # for i in range(L):
    #     s.add(Or([cv[j]==(cv[i]+1)%L for j in gr[i]]))
