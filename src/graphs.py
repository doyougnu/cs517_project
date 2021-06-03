"""
- Module    : graphs.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines sample graphs
"""

import igraph as ig
import networkx as nx

rrg  = { 0: [1,2,3,4,5],
         1: [2,5],
         2: [3,4],
         3: [4,5],
         4: [1],
         5: [4,2]
        }

round_robin_graph = ig.Graph(edges = [(v, e) for v in rrg.keys() for e in rrg[v]], directed=True)

round_robin_nx = round_robin_graph.to_networkx()

aag = { 0: [1],
        1: [2,3],
        2: [0],
        3: [4],
        4: [5],
        5: [3,2]
      }

anti_greed_graph = ig.Graph(edges = [(v,e) for v in aag.keys() for e in aag[v]], directed=True)

anti_greed_nx = anti_greed_graph.to_networkx()

tri = {0 : [1],
       1 : [2],
       2 : [0]
       }

triangle_cycle = ig.Graph(edges =[(v,e) for v in tri.keys() for e in tri[v]], directed=True)
