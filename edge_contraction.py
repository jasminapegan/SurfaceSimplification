"""
    The edge contraction algorithm removes an edge〈a, b〉in the triangulation and replaces it with a new vertex c
    (and modifies the triangulation around the vertex c). This operation is only allowed if the topological type of
    the surface is not altered by the modification. This can be checked by comparing the link of the the edge〈a, b〉
    and the links of the vertices a and b.

    Literature: Computational Topology, pages 52 - 57

    Data source: http://graphics.stanford.edu/data/3Dscanrep/
"""
from helpers import triangle_normal
import numpy as np


def edge_contraction(graph, edge):
    """ Edge contraction algorithm. """
    pass


def contract(graph, edge):
    """ Simulates removal of edge '(a, b)' and added new node 'c'. Does not correct the graph.
        Returns 'c',  'x' and 'y' which were in ex-triangles '(a, b, x)' and '(a, b, y)'.
    """
    pass


def initial_error(graph, triangulation, points):
    error = {}

    error_points = [0 for _ in graph.nodes]
    for i in graph.nodes():
        error[(i,)] = 0

    error_edges = [0 for _ in graph.edges]
    for e in graph.edges():
        error[e] = 0

    error_triangles = [0 for _ in triangulation]
    for t in triangulation:
        error[tuple(t)] = 0

    # Qabx
    for i, triangle in enumerate(triangulation):
        a, b, c = triangle

        u = triangle_normal(points[a], points[b], points[c])
        error_triangles[i] = np.dot(u, np.transpose(u))
        error[triangle] = triangle_normal(points[a], points[b], points[c])

        for x in (a, b, c):
            for y in (a, b, c):
                # we visit each pair once (x < y is unique pair)
                if x < y:

                    # Qab
                    error_edges[graph.edges.index((x, y))] += error_triangles[i]
                    error[(x, y)] += error_triangles[i]

                    # Qa
                    error_points[graph.nodes.index(x)] += 0  # todo
                    error[(x,)] += error[(x, y)]
                    error[(y,)] += error[(x, y)]

            error[(x,)] += error[triangle]

    return error


def deformation_error(graph, error, edge):
    """ Score that measures how deformed the graph becomes by contracting the edge. """
    a, b = edge

    # get the new point and new edges from somewhere
    c, x, y = contract(graph, edge)

    # avoid calculating twice
    if (c,) not in error.keys():
        error[(c,)] = error[(a,)] + error[(b,)] - error[edge]
        error[(c, x)] = error[(a, x)] + error[(b, x)] - error[(a, b, x)]
        error[(c, y)] = error[(a, y)] + error[(b, y)] - error[(a, b, y)]

    return error[(a, b)]


def error_contract(error, edge):
    """ Removes edge data from error dictionary to save space. """
    error.pop(edge, None)
    error.pop((edge[0],), None)
    error.pop((edge[1],), None)


def link_of_edge(graph, edge):
    neigh_a = set(graph.neighbors(edge[0]))
    neigh_b = set(graph.neighbors(edge[1]))
    return neigh_a.intersection(neigh_b)


def link_of_node(graph, a):
    neigh_a = set(graph.neighbors(a))
    edges_a = set(graph.edges(a))
    return neigh_a.union(edges_a)


def sort_edges(triangulation):
    """ Sort edges in triangulation according to deformation to graph. """
    pass

