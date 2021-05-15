"""
- Module    : graphs.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines sample graphs
"""


round_robin_graph = { "A": ["B","C","D","E","F"],
                      "B": ["C","F"],
                      "C": ["D","E"],
                      "D": ["E","F"],
                      "E": ["B"],
                      "F": ["E","C"]
                    }

anti_greed_graph = { 0: [1],
                     1: [2,3],
                     2: [0],
                     3: [4],
                     4: [5],
                     5: [3,2]
                   }
