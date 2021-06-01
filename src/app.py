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

    matrix     = graph.get_adjacency()
    n,c = matrix.shape
    sym_matrix = [[0] * n] * c

    def symbolize(i,j):
        s = z.Int('edge_{0}{1}'.format(i,j))
        return s

    def value_of(i,j):
        return matrix[i][j]

    def constraint_1(i,j,k):
        y_ij = value_of(i,j)
        y_jk = value_of(j,k)
        y_ik = value_of(i,k)

        s.add((y_ij + y_jk - y_ik) <= 1)

    def constraint_2(i,j,k):
        y_ij = value_of(i,j)
        y_jk = value_of(j,k)
        y_ik = value_of(i,k)

        s.add((-y_ij - y_jk + y_ik) <= 0)

    def constraint_3(symbolic, value):
        s.add(symbolic == value)

    def int_formulation(j):
        left = z.Int("sum_j-1")
        left = z.Sum([sym_matrix[k][j] for k in range(j-1)])

        right = z.Int("sum_n")
        right = z.Sum([1 - sym_matrix[j][l] for l in range(j+1,n)])

        return [left, right]


    ## Iteration for triangle properties
    for n in range(n):
        for k in range(n):
            for j in range(k):
                for i in range(j):
                    constraint_1(i,j,k)
                    constraint_2(i,j,k)


    ## constraint 3, every edge must be a 0 or a 1, we get the 0 or 1 directly
    ## from the adjacency matrix
    for i in range(n):
        for j in range(len(matrix[i])):
            s_edge = symbolize(i,j)
            sym_matrix[i][j] = s_edge
            constraint_3(s_edge, matrix[i][j])


    ## minimization
    o = z.Optimize()
    y = z.Int('y')

    pprint(u.flatten([int_formulation(j) for j in range(n)]))
    y = z.Sum(u.flatten([int_formulation(j) for j in range(n)]))
    o.minimize(y)

    r = []
    m = []

    done = False

    # while not done:
    if s.check() == z.sat:
        m = s.model()
        r.append(m)
    else:
        done = True

    return r

def runWithGraph(s,graph):
    # flag to end loop
    done = False

    # kick off
    while not done:

        # get the core
        cores = find_cycles_by_matrices(s, graph)

        # if the core is empty then we are done, if not then relax and recur
        print("Core: ", cores)

        done = True

    return graph

def run():
    # spin up the solver
    s = z.Solver()

    g = gs.anti_greed_graph
    newG = runWithGraph(s,g)
    print("Is new G a Dag? ", newG.is_dag())
    return u.edge_to_list_dict(newG)
