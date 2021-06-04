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
import numpy    as np

import matplotlib.pyplot as plt

import gadgets as g
import graphs  as gs
import utils   as u

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

def relax(solver, sgraph, core, strategy):
    s_edge = u.parse_edge(strategy(core))
    solver.add(s_edge == 0)


def find_all_cycles(s,graph):
    """Find a cycle in a graph. s is a solver object, graph is an igraph object.
    Given the graph iterate over the graph, convert the key and values to
    symbolic terms and check for a cycle. Returns the unsat core as a list of
    strings e.g. [1->2, 2->3, 3->4, 4->1]

    I'm leaving this here just to try to get the abstract hamiltonian cycle
    constrain working.
    """

    grph     = u.edge_to_list_dict(graph)
    node_cnt = len(grph)
    k        = z.Int("k")
    syms     = [z.Int('node%s'%i) for i in range(node_cnt)]

    # s.add(syms[0] == 0) # start node is a 0
    s.add(k < node_cnt)
    s.add(k > 1)

    o = z.Optimize()

    # for source, sinks in sgraph.s_adj_list():
    for i in range(node_cnt):
        s.add(syms[i] >= 0)
        s.add(syms[i] <= k)
        s.add(z.Or([syms[j] == ((syms[i] + 1) % k) for j in grph[i]]) == (syms[i] == 0))


    r = []
    m = []

    # o.minimize(z.Sum([syms[i] for i in range(node_cnt)]))
    s.add(z.Product([syms[i] for i in range(node_cnt)]) == 0)
    done = False
    while not done:
        if s.check() == z.sat:
            m = s.model()
            r.append(m)
            s.add(k != m[k])
        else:
            done = True

    return r

def find_cycles_by_matrices(s,graph):
    """Define two matrices, one for weights and one for (i,j) pairs. If i comes
    before j then leave (i,j) greater than 0 but unbound, when we want to relax
    an edge we set it to 1. Then add a constraint that the sum of every edge in
    the graph must be equal to 0.
    """

    ## initialization
    matrix      = graph.get_adjacency()
    n, c        = matrix.shape
    sym_matrix  = np.empty((n,c), dtype=object)
    # cost_matrix = np.zeros((n,c))
    cache       = {}

    def symbolize(i,j):
        "given two indices, create a symbolic variable"
        s = z.Int('edge_{0}{1}'.format(i,j))
        return s


    def value_of(i,j):
        "given two indices, return the (i,j)th value in the adjacency matrix"
        return sym_matrix[i][j]


    def constraint_1(n,i,j,k):
        y_ij = value_of(i,j)
        y_jk = value_of(j,k)
        y_ik = value_of(i,k)

        name       = "c1" + str((n,i,j,k))
        constraint = (y_ij + y_jk - y_ik) <= 1

        # if name not in cache:
        #     cache[name] = constraint
        s.assert_and_track(constraint, name)


    def constraint_2(n,i,j,k):
        y_ij = value_of(i,j)
        y_jk = value_of(j,k)
        y_ik = value_of(i,k)

        name       = "c2" + str((n,i,j,k))
        constraint = (-y_ij - y_jk + y_ik) <= 0

        # if name not in cache:
        #     cache[name] = constraint
        s.assert_and_track(constraint, name)


    def constraint_3(symbolic):
        s.add(z.Or([symbolic == 0, symbolic == 1]))


    def int_formulation(j):
        left  = z.Sum([matrix[k][j] * sym_matrix[k][j] for k in range(j)])
        right = z.Sum([matrix[l][j] * (1 - sym_matrix[j][l]) for l in range(j+1, n)])

        return [left, right]


    ## constraint 3, every edge must be a 0 or a 1, we get the 0 or 1 directly
    ## from the adjacency matrix
    ## we do this first so that the sym_matrix is populated
    for n_iter in range(n):
        for j in range(n_iter+1):
            for i in range(j):
                s_edge           = symbolize(i,j)
                sym_matrix[i][j] = s_edge
                constraint_3(s_edge)

    ## Iteration for triangle inequalities
    for n_iter in range(n):
        for k in range(n_iter+1):
            for j in range(k):
                for i in range(j):
                    constraint_1(n_iter,i,j,k)
                    constraint_2(n_iter,i,j,k)


    ## minimization
    o = z.Optimize()
    y = z.Int('y')

    y = z.Sum(u.flatten([int_formulation(j) for j in range(n)]))
    o.minimize(y)

    cores = []
    m = []

    done = False

    # while not done:
    if s.check() == z.sat:
        print(s.check())
        cores = s.model()
    else:
        cores = s.unsat_core()
        done = True

    return cores


def MFAS_set_cover(s,graph):
    """ TODO
    """

    ## initialization
    m            = graph.ecount()
    cycle_matrix = u.mk_cycle_matrix(u.find_all_cycles(graph), m)
    n, c         = graph.get_adjacency().shape
    num_cycles   = len(cycle_matrix)
    edge_list    = graph.get_edgelist()
    cache        = {}


    def symbolize(i,j):
        "given two indices, create a symbolic variable"
        s = z.Int('edge_{0}{1}'.format(i,j))
        return s


    def constraint_1(i,s_edge):
        edge = cache[s_edge]
        value = 0
        if edge in cycle_matrix[i]:
            value = cycle_matrix[i][edge]

        return (value * s_edge)


    ## symbolize the edges
    for source,sink in edge_list:
            s_edge        = symbolize(source, sink)
            cache[s_edge] = (source,sink)


    ## constraint 1
    s.add(z.Sum([constraint_1(i,s_edge)
                 for i in range(num_cycles)
                 for s_edge in cache.keys()]) >= 1)


    ## minimization
    o = z.Optimize()
    y = z.Int('y')

    ## y can only be a 1 or a 0
    s.add(z.Or([y == 0, y == 1]))

    ## y is the sum of symbolic edges
    y = z.Sum(list(cache.keys()))

    ## we want the smallest y possible
    o.minimize(y)

    # # while not done:
    if s.check() == z.sat:
        cores = s.model()
    else:
        cores = s.unsat_core()
        done = True

    return cores


def runWithGraph(s,graph):
    # flag to end loop
    done = False

    # kick off
    # while not done:

        # get the core
    cores = MFAS_set_cover(s, graph)

    return cores

def main():
    # spin up the solver
    s = z.Solver()

    g = gs.anti_greed_graph
    return runWithGraph(s,g)
