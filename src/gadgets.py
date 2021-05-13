"""
- Module    : Gadgets.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which defines gadgets for minimum feedback arc set encoding to SAT
"""

from z3 import *

x = Bool("x")
y = Bool("y")
x_or_y = Or([x,y])

s = Solver()
s.add(x_or_y)
s.check()
s.model()
