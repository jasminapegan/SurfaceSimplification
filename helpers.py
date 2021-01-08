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


def error_triangle(a, b, c, points):
    u = triangle_normal2(points[a], points[b], points[c])
    return np.outer(u, np.transpose(u))


def sorted_tuple(*lst):
    return tuple(sorted(lst))


def homology(triangulation):
    pass
