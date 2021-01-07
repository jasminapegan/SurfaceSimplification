"""
    Plots and homology helper functions.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import networkx as nx
import gudhi


def plot(triangulation, points):
    x, y, z = map(list, zip(*points))
    triang = mtri.Triangulation(x, y, triangles=triangulation)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(triang, z)
    plt.show()


def triangulation_to_graph(triangulation, points):
    graph = nx.Graph()

    # nodes are indices of points
    for i, point in enumerate(points):
        graph.add_node(i)
        # add also coordinate data
        #graph.nodes[i]['pos'] = point

    # add the links in triangles
    for a, b, c in triangulation:
        graph.add_edges_from([(a, b), (b, c), (a, c)])

    return graph


def triangle_normal(a, b, c):
    ab = np.array(b) - np.array(a)
    ac = np.array(c) - np.array(a)
    cross = np.cross(ab, ac)
    return cross / np.linalg.norm(cross)


def triangle_normal2(a, b, c):
    ab = np.array(b) - np.array(a)
    ac = np.array(c) - np.array(a)
    cross = np.cross(ab, ac)
    cross = cross / np.linalg.norm(cross)
    d = -cross.dot(a)
    return np.append(cross,d)

def c_coordinate(e,error,points):
    a, b = e
    edge_error = error[(a,)] + error[(b,)]
    try:
        c = np.linalg.solve(edge_error[:-1, :-1], -edge_error[:-1, -1])
    except np.linalg.LinAlgError:
        a, b = e
        a_coordinate = points[a]
        b_coordinate = points[b]
        c = (np.array(a_coordinate) + np.array(b_coordinate)) / 2
    return c,edge_error

def triangle_error(a,b,c):
    u = triangle_normal2(a,b,c)
    return np.outer(u,u)


"""def derivative(Q, i, x):
    QTx = np.matmul(np.transpose(Q[i]), x)
    xTQ = np.matmul(np.transpose(x), Q[i])
    return np.add(QTx, xTQ)"""

def solve_system(Q):
    """ This needs to be checked, no idea if it's correct """
    return np.linalg.solve(Q, 0)


def sorted_tuple(*lst):
    return tuple(sorted(lst))


def homology(triangulation):
    pass
