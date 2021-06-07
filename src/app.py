"""- Module    : app.py
- Copyright : (c) Jeffrey M. Young
            ; (c) Colin Shea-Blymyer
- License   : BSD3
- Maintainer: youngjef@oregonstate.edu, sheablyc@oregonstate.edu
- Stability : experimental

Module which encodes the constraints to the solver

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

import graphs  as gs
import utils   as u

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

def find_topo_order(s,graph):
    """Define two matrices, one for weights and one for (i,j) pairs. If i comes
    before j then leave (i,j) greater than 0 but unbound, when we want to relax
    an edge we set it to 1. Then add a constraint that the sum of every edge in
    the graph must be equal to 0, thus any edge constrained to be 1 cannot be
    considered and the solver makes progess.
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

    result = []

    if s.check() == z.sat:
        result = s.model()

    return result


def MFAS_set_cover(s,graph):
    """Find the minimum feedback arc set by encoding it as a minimum set cover.
    The encoding requires a cycle matrix which we find externally to the SAT
    solver. Then given the cycle matrix we do the following encoding:

    Variables:
      - m is |E|
      - w_{j} is the weight of edge j \in E
      - y_{j} is a symbolic edge; y_{j} = 1 if edge j is in the feedback edge set and 0 otherwise
      - a is the cycle matrix
      - a_{ij} is the value of edge j in cycle i; a_{ij} = 1 if j participates, 0 otherwise


    minimize(sum{j = 1}^{m}(w_{j} * y_{j}))

      subject to:

    sum_{j = 1}^{m}(a_{ij} * y_{j}) >= 1
    \forall i. y_{i} \in {0,1}
    """

    ## initialization
    m            = graph.ecount()
    cycle_matrix = u.mk_cycle_matrix(u.find_all_cycles(graph), m)
    n, c         = graph.get_adjacency().shape
    num_cycles   = len(cycle_matrix)
    edge_list    = graph.get_edgelist()
    sym_to_edge_cache = {}
    edge_to_sym_cache = {}
    sum_var      = 'y'


    def symbolize(i,j):
        "given two indices, create a symbolic variable"
        new = z.Int('{0}->{1}'.format(i,j))
        return new


    def constraint_1(i,s_edge):
        """ Multiply the edge by its corresponding value in the cycle matrix
        """
        edge  = sym_to_edge_cache[s_edge]
        value = 0
        if edge in cycle_matrix[i]:
            value = cycle_matrix[i][edge]

        return (value * s_edge)


    ## symbolize the edges
    for source,sink in edge_list:
            s_edge                           = symbolize(source, sink)
            ## an edge is either a 0 or a 1
            s.add(z.Or([s_edge == 0, s_edge == 1]))

            sym_to_edge_cache[s_edge]        = (source,sink)
            edge_to_sym_cache[(source,sink)] = s_edge


    ## Perform constraint 1 and add it to the solver instance
    for i in range(num_cycles):
        s.add(z.Sum([constraint_1(i,s_edge)
                     for s_edge in sym_to_edge_cache.keys()]) >= 1)


    ## we want the smallest y possible
    s.minimize(z.Sum([s_edge for s_edge in sym_to_edge_cache.keys()]))

    s.check()
    return s.model()


def runWithGraph(graph):
    s = z.Optimize()
    return MFAS_set_cover(s, graph), u.get_feedback_arc_set(graph)


def runErdosRenyi(n,p):
    """Given n vertices and a probability, p of edges. Find the minimum
    feedback arc set of an erdos-renyi graph

    """
    s = z.Optimize()
    g = ig.Graph.Erdos_Renyi(n, p, directed=True, loops=True)
    return MFAS_set_cover(s,g), u.get_feedback_arc_set(g)


def runWattsStrogatz(dim, size, nei, p):
    """Given the dimension of the lattice, size of the lattice along all
    dimensions, the number of steps within which two vertices are connected
    (nei), and the probability p, find the minimum feedback arc set of a
    watts-strogatz graph

    """
    s = z.Optimize()
    g = ig.Graph.Watts_Strogatz(dim, size, nei, p, loops=True, multiple=False)
    return MFAS_set_cover(s,g), u.get_feedback_arc_set(g)

############################# Benchmarks #####################################
def test_erdos_renyi(benchmark):
    benchmark(runErdosRenyi(10,0.2))
