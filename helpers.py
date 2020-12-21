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


def homology(triangulation):
    pass
