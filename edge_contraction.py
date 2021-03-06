"""
    The edge contraction algorithm removes an edge〈a, b〉in the triangulation and replaces it with a new vertex c
    (and modifies the triangulation around the vertex c). This operation is only allowed if the topological type of
    the surface is not altered by the modification. This can be checked by comparing the link of the the edge〈a, b〉
    and the links of the vertices a and b.

    Literature: Computational Topology, pages 52 - 57

    Data source: http://graphics.stanford.edu/data/3Dscanrep/
"""
from helpers import sorted_tuple, c_coordinate, error_triangle
import numpy as np
from queue import PriorityQueue


def edge_contraction(graph, triangulation, points):
    """ Edge contraction algorithm.
     First calculate initial errors and sort edges according to the error in priority queue.
     While priority queue is not empty, get edge with highest priority, update graph and update triangulation.  """
    error = initial_quadrics(graph, triangulation, points)
    edges_errors_pq, edge_coordinate = sort_edges(graph, error,points)

    while not edges_errors_pq.empty():
        err, edge = edges_errors_pq.get()
        if is_safe(graph, edge):
            points.append(edge_coordinate[edge])
            removed, added = contract(graph, edge, triangulation, points)
            quadrics_contract_before(graph, error, edge, points, removed, added)

            for e in removed.get('edges'):
                graph.remove_edge(*e)
            for n in removed.get('nodes'):
                graph.remove_node(n)
            for t in list(set(removed.get('triangles'))):
                if t not in triangulation:
                    return triangulation, points
                triangulation.remove(t)

            for n in added.get('nodes'):
                graph.add_node(n)
            for e in added.get('edges'):
                graph.add_edge(*e)
            for t in list(set(added.get('triangles'))):
                triangulation.append(t)

            quadrics_contract_after(error, edge, triangulation, added['edges'])

            for e in added.get('edges'):
                c, edge_error = c_coordinate(e, error, points)
                edge_coordinate.update({e: c})
                c_error = np.append(c, 1)
                pq_error = np.dot(np.dot(c_error, edge_error), np.transpose(c_error))
                edges_errors_pq.put((pq_error, e))
    return triangulation, points


def contract(graph, edge, triangulation, points):
    """ Simulates removal of edge '(a, b)' and added new node 'c'. Does not correct the graph.

        What it does:
        - Nodes a and b are removed, c is added.
        - All neighbors of 'a' and 'b' become neighbors of 'c'. (Remove (a,*), (b,*) and add (c,*))
          This is: for all nodes x in Link(a,b) except a, b: add (c, x).
        - All triangles with a and b are removed.
          Added: for y in Link(a) U Link(b): for x in Link(c,y): triangle (c, x, y)

        Returns two dicts of lists of added stuff and list of removed stuff.
        Ex.:
            added = {'nodes': [(1,)], 'edges': [(1,2), (1,3)], 'triangles': [(1,2,3)]}
            removed = {'nodes': [(4,)], 'edges': [(2,4), (3,4)], 'triangles': [(2,3,4)]}
    """
    removed = {'nodes': [], 'edges': [], 'triangles': []}
    added = {'nodes': [], 'edges': [], 'triangles': []}

    a, b = edge
    c = len(points) - 1

    Lk_a = link_of_node(graph, a)
    Lk_b = link_of_node(graph, b)
    Lk_ab = link_of_edge(graph, edge)

    # Nodes a and b are removed, c is added.
    removed['nodes'].append(a)
    removed['nodes'].append(b)
    added['nodes'].append(c)

    # All neighbors of 'a' and 'b' become neighbors of 'c'. (Remove (a,*), (b,*) and add (c,*))
    # This is: for all nodes x in Link(a,b) except a, b: add (c, x)
    for x in Lk_ab:
        removed['edges'].append(sorted_tuple(a, x))
        removed['edges'].append(sorted_tuple(b, x))
        added['edges'].append(sorted_tuple(c, x))

    # I added this - we need to update as well all edges incident to a : remove (a,*) and add (c,*)
    # I did it by updating nodes and it can be done also by updting edges (if instance is tuple), it doesn't matter
    for x in Lk_a:
        if isinstance(x, int) and x != b and (x not in Lk_ab):
            removed['edges'].append(sorted_tuple(a, x))
            added['edges'].append(sorted_tuple(c, x))
    # I added this - we need to update as well all edges incident to b : remove (b,*) and add (c,*)
    for x in Lk_b:
        if isinstance(x, int) and x != a and (x not in Lk_ab):
            removed['edges'].append(sorted_tuple(b, x))
            added['edges'].append(sorted_tuple(c, x))

    # All triangles with a and b are removed.
    # Added: for x, y in Link(a) U Link(b): for x in Link(c,y): triangle (c, x, y)
    for x in Lk_ab:
        #if sorted_tuple(a, b, x) in triangulation:
        removed['triangles'].append(sorted_tuple(a, b, x))

    # We also need to remove from triangulation all triangles that had a or b as node
    # and to add instead of that all tringles having other two coordinates same as before plus c instead of a or b
    # This commented code below is instead of part from line 202 - to remove and append proper triangles to triangulation
    """
    for i,j,k in triangulation:
        if (i == a and j != b and k != b) or (i == b and j != a and k != a):
              removed['triangles'].append(sorted_tuple(i,j,k))
              added['triangles'].append(sorted_tuple(c,j,k))
        if (i != a and j == b and k != a) or (i != b and j == a and k != b):
              removed['triangles'].append(sorted_tuple(i,j,k))
              added['triangles'].append(sorted_tuple(i,c,k))
        if (i != b and j != b and k == a) or (i != a and j != a and k == b):
              removed['triangles'].append(sorted_tuple(i, j, k))
              added['triangles'].append(sorted_tuple(i, j, c))
    """
    for t in triangulation:
        difference = set(t).difference({a, b})
        if len(difference) == 2:
            removed['triangles'].append(sorted_tuple(*t))
            added['triangles'].append(sorted_tuple(*difference, c))

    return removed, added


def initial_quadrics(graph, triangulation, points):
    quadrics = {}

    for i in graph.nodes():
        quadrics[(i,)] = np.array([[0 for _ in range(4)] for _ in range(4)])

    for e in graph.edges():
        quadrics[sorted_tuple(*e)] = np.array([[0 for _ in range(4)] for _ in range(4)])

    for t in triangulation:
        quadrics[sorted_tuple(*t)] = np.array([[0 for _ in range(4)] for _ in range(4)])

    # Qabx
    for i, triangle in enumerate(triangulation):
        a, b, c = triangle
        quadrics[sorted_tuple(*triangle)] = error_triangle(a, b, c, points)

        for x in (a, b, c):
            for y in (a, b, c):
                # we visit each pair once (x < y is unique pair)
                if x < y:

                    # Qab
                    if sorted_tuple(x, y) not in quadrics.keys():
                        quadrics[sorted_tuple(x, y)] = np.array([[0 for _ in range(4)] for _ in range(4)])
                    quadrics[sorted_tuple(x, y)] = np.add(quadrics[sorted_tuple(x, y)], quadrics[sorted_tuple(*triangle)])

                    # Qa
                    #if (x,) not in quadrics.keys():
                    #    quadrics[(x,)] = np.array([[0 for _ in range(4)] for _ in range(4)])
                    #quadrics[(x,)] = np.add(quadrics[(x,)], quadrics[sorted_tuple(x, y)])

                    #if (y,) not in quadrics.keys():
                    #    quadrics[(y,)] = np.array([[0 for _ in range(4)] for _ in range(4)])
                    #quadrics[(y,)] = np.add(quadrics[(y,)], quadrics[sorted_tuple(x, y)])

            if (x,) not in quadrics.keys():
                quadrics[(x,)] = np.array([[0 for _ in range(4)] for _ in range(4)])
            quadrics[(x,)] = np.add(quadrics[(x,)], quadrics[sorted_tuple(*triangle)])

    return quadrics


def quadrics_contract_before(graph, quadrics, edge, points, removed, added):
    """ Score that measures how deformed the graph becomes by contracting the edge. """
    a, b = sorted_tuple(*edge)

    # error of new point -- there is only one added point when contracting an edge
    c = added['nodes']
    if len(c) != 1:
        raise Exception("Contraction should result in only one point.")
    c = c[0]
    quadrics[(c,)] = np.subtract(np.add(quadrics[(a,)], quadrics[(b,)]), quadrics[sorted_tuple(a, b)])

    # error of new edges by formula -- we need to calculate this before removing edges and triangles
    x, y = link_of_edge(graph, (a, b))
    t1, t2 = sorted_tuple(a, b, x), sorted_tuple(a, b, y)
    if t1 not in quadrics.keys():
        return
        quadrics[t1] = error_triangle(*t1, points)
    if t2 not in quadrics.keys():
        quadrics[t2] = error_triangle(*t2, points)

    quadrics[sorted_tuple(c, x)] = np.subtract(np.add(quadrics[sorted_tuple(a, x)], quadrics[sorted_tuple(b, x)]), quadrics[sorted_tuple(a, b, x)])
    quadrics[sorted_tuple(c, y)] = np.subtract(np.add(quadrics[sorted_tuple(a, y)], quadrics[sorted_tuple(b, y)]), quadrics[sorted_tuple(a, b, y)])

    # error of new triangles -- the easiest to calculate, doesn't need other errors
    for triangle in added["triangles"]:
        quadrics[sorted_tuple(*triangle)] = error_triangle(*triangle, points)

    # remove old points
    for n in removed["nodes"]:
        quadrics.pop(n, None)

    # remove old edges
    for e in removed["edges"]:
        quadrics.pop(e, None)

    # remove old triangles
    for t in removed["triangles"]:
        quadrics.pop(t, None)

def quadrics_contract_after(error, edge, triangulation, added_edges):
    # error of other edges -- we need new triangles and should not use old ones here
    for e in added_edges:
        if e != edge:
            error[sorted_tuple(*e)] = np.array([[0 for _ in range(4)] for _ in range(4)])
            for x, y, z in triangulation:
                if set(e).issubset({x, y, z}):
                    error[sorted_tuple(*e)] = np.add(error[sorted_tuple(*e)], error[sorted_tuple(x, y, z)])

def link_of_edge(graph, edge):
    neigh_a = set(graph.neighbors(edge[0]))
    neigh_b = set(graph.neighbors(edge[1]))
    return neigh_a.intersection(neigh_b)


def link_of_node(graph, a):
    neigh_a = set(graph.neighbors(a))
    edges_a = set(graph.edges(a))
    return neigh_a.union(edges_a)


def sort_edges(graph, error,points):
    """ Sort edges in triangulation according to deformation to graph. """
    error_edge_pq = PriorityQueue()
    edge_c_dict=dict()

    for e in graph.edges():
        c , edge_error=c_coordinate(e,error,points)
        edge_c_dict.update({e:c})
        c_error = np.append(c,1)
        pq_error = np.dot(np.dot(c_error,edge_error),np.transpose(c_error))
        error_edge_pq.put((pq_error, e))

    return error_edge_pq, edge_c_dict


def is_safe(graph, edge):
    """ Check if contraction of an edge preserves the topological type """

    if graph.has_edge(*edge):
        edge_link = link_of_edge(graph, edge)
        edge_v1_link = link_of_node(graph, edge[0])
        edge_v2_link = link_of_node(graph, edge[1])

        if edge_link == (edge_v1_link.intersection(edge_v2_link)) and len(list(edge_link)) == 2:
            return True

    return False


"""
def get_triangle_order_in_triangulation(point, triangulation):
    a, b, c = point
    if (a, b, c) in triangulation:
        return (a, b, c)
    if (a, c, b) in triangulation:
        return (a, c, b)
    if (b, c, a) in triangulation:
        return (b, c, a)
    if (b, a, c) in triangulation:
        return (b, a, c)
    if (c, a, b) in triangulation:
        return (c, a, b)
    if (c, b, a) in triangulation:
        return (c, b, a)

def deformation_error_edge(graph, error, edge, triangulation, points):
    # Score that measures how deformed the graph becomes by contracting the edge. 
    a, b = sorted_tuple(*edge)
    newErrs = dict()

    # get the new point and new edges from somewhere
    removed, added = contract(graph, edge, triangulation, points)

    # error of new point -- there is only one added point when contracting an edge
    c = added['points']
    if len(c) != 1:
        raise Exception("Contraction should result in only one point.")
    c = c[0]
    newErrs[(c,)] = np.diff(np.add(error[(a,)], error[(b,)]), error[sorted_tuple(a, b)])

    # error of new edges by formula -- we need to calculate this before removing edges and triangles
    x, y = link_of_edge(graph, (a, b))
    newErrs[sorted_tuple(c, x)] = np.diff(np.add(error[sorted_tuple(a, x)], error[sorted_tuple(b, x)]), error[sorted_tuple(a, b, x)])
    newErrs[sorted_tuple(c, y)] = np.diff(np.add(error[sorted_tuple(a, y)], error[sorted_tuple(b, y)]), error[sorted_tuple(a, b, y)])

    # error of new triangles -- the easiest to calculate, doesn't need other errors
    for t in added["triangles"]:
        newErrs[t] = error_triangle(*t, points) # triangle_normal2(*t)

    # error of other edges -- we need new triangles and should not use old ones here
    for e in added["edges"]:
        if e != edge:
            newErrs[sorted_tuple(*e)] = np.array([[0 for _ in range(4)] for _ in range(4)])

            # add errors from old nonremoved triangles
            for x, y, z in triangulation:
                if sorted_tuple(x, y, z) not in removed["triangles"]:
                    if x in e and y in e or x in e and z in e or y in e and z in e:
                        newErrs[sorted_tuple(*e)] = np.add(error[sorted_tuple(*e)], error[sorted_tuple(x, y, z)])

            # add errors from new triangles
            for x, y, z in added["triangles"]:
                if x in e and y in e or x in e and z in e or y in e and z in e:
                    newErrs[sorted_tuple(*e)]= np.add(error[sorted_tuple(*e)], error[sorted_tuple(x, y, z)])

    return newErrs[sorted_tuple(a, b)]
    
    

def deformation_error(graph, error, edge, triangulation, points):
    # Score that measures how deformed the graph becomes by contracting the edge. 
    a, b = sorted_tuple(*edge)

    # get the new point and new edges from somewhere
    # c, x, y = contract(graph, edge, points)
    removed, added = contract(graph, edge, triangulation, points)
    c = added['points'][0]

    # avoid calculating twice
    #if c not in error.keys():
    error[c] = error[(a,)] + error[(b,)] - error[sorted_tuple(a, b)]

    x, y = link_of_edge(graph, (a, b))
    error[sorted_tuple(c, x)] = error[sorted_tuple(a, x)] + error[sorted_tuple(b, x)] - error[sorted_tuple(a, b, x)]
    error[sorted_tuple(c, y)] = error[sorted_tuple(a, y)] + error[sorted_tuple(b, y)] - error[sorted_tuple(a, b, y)]

    return error[sorted_tuple(a, b)]
    
    
def initial_error(graph, triangulation, points):
    error = {}

    for i in graph.nodes():
        error[(i,)] = 0

    for e in graph.edges():
        error[sorted_tuple(*e)] = 0

    for t in triangulation:
        error[sorted_tuple(*t)] = 0

    error_triangles = [0 for _ in triangulation]

    # Qabx
    for i, triangle in enumerate(triangulation):
        error_triangles[i] = error_triangle(*triangle, points)
        error[triangle] = error_triangle(*triangle, points)

        for x in triangle:
            for y in triangle:
                # we visit each pair once (x < y is unique pair)
                if x < y:

                    # Qab
                    if (x, y) not in error.keys():
                        error[(x, y)] = 0
                    error[(x, y)] += error_triangles[i]

                    # Qa
                    if (x,) not in error.keys():
                        error[(x,)] = 0
                    error[(x,)] += error[(x, y)]

                    if (y,) not in error.keys():
                        error[(y,)] = 0
                    error[(y,)] += error[(x, y)]

            if (x,) not in error.keys():
                error[(x,)] = 0
            error[(x,)] += error[sorted_tuple(*triangle)]

    return error


"""