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
from sortedcontainers import SortedDict


def edge_contraction(graph,triangulation,points):
    """ Edge contraction algorithm.
     First calculate initial errors and sort edges according to the error in priority queue.
     While priority queue is not empty, get edge with highest priority, update graph and update triangulation.  """
    error=initial_error(graph,triangulation,points)
    edges_errors_pq=sort_edges(graph,error)
    err,edge=edges_errors_pq.popitem()

    while edges_errors_pq:
        if(is_safe(graph,edge)):
            a, b = edge
            link_a=link_of_node(graph,a)
            link_b=link_of_node(graph,b)
            c,x,y=contract(graph, edge)

            #update graph
            #by removing nodes we remove all incident edges as well
            graph.remove_node(a)
            graph.remove_node(b)
            graph.add_node(c)
            for v in list(link_a):
                if isinstance(v, int):
                     graph.add_edge(v,c)
            for v in list(link_b):
                if isinstance(v, int):
                     graph.add_edge(v,c)

            # update triangulation by removing triangles a,b,x and a,b,y (could there be problem with order?)
            # and in all other triangles replace a and b with c
            triangulation.remove((a,b,x))
            triangulation.remove((a,b,y))
            for i,j,k in triangulation:
                if (i==a or i==b):
                    triangulation.remove(i,j,k)
                    triangulation.append(c,j,k)
                if (j==a or j==b):
                    triangulation.remove(i,j,k)
                    triangulation.append(i,c,k)
                if (k==a or k==b):
                    triangulation.remove(i,j,k)
                    triangulation.append(i,j,c)

        err, edge = edges_errors_pq.popitem()

    return triangulation

def contract(graph, edge,points):
    """ Simulates removal of edge '(a, b)' and added new node 'c'. Does not correct the graph.
        Returns 'c',  'x' and 'y' which were in ex-triangles '(a, b, x)' and '(a, b, y)'.
    """
    a, b = edge
    a_coordinate=points[a]
    b_coordinate=points[b]
    c_coordinate=(a_coordinate+b_coordinate)/2

    points.append(c_coordinate)
    # obtain c label -> again to enumerate or b length -> should we update triangulation and points or not?
    c=len(points)
    #the code will ensure that lenth of link_of_edge(graph, edge) is 2 but maybe to check again ?
    x,y = tuple(list(link_of_edge(graph, edge)))

    return c,x,y


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


def sort_edges(graph,error):
    """ Sort edges in triangulation according to deformation to graph. """
    #TO DO: test if it sorts ascending or descending  (error->-error)
    error_edge_pq=SortedDict()
    for e in graph.edges():
        edge_error=error[e]
        error_edge_pq[edge_error]=e

    return error_edge_pq

def is_safe(graph,edge):
    """ Check if contraction of an edge preserves the topological type """
    edge_link=link_of_edge(graph,edge)
    edge_v1_link=link_of_node(graph,edge[0])
    edge_v2_link = link_of_node(graph, edge[1])

    if(edge_link==(edge_v1_link.intersection(edge_v2_link))):
        return True

    return False
