"""
- Module    : graphs.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines sample graphs
"""

import networkx as nx

round_robin_graph = nx.DiGraph({ "A": ["B","C","D","E","F"],
                                 "B": ["C","F"],
                                 "C": ["D","E"],
                                 "D": ["E","F"],
                                 "E": ["B"],
                                 "F": ["E","C"]
                               })

anti_greed_graph = nx.DiGraph({ 0: [1],
                                1: [2,3],
                                2: [0],
                                3: [4],
                                4: [5],
                                5: [3,2]
                              })
