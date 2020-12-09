"""
    The edge contraction algorithm removes an edge〈a, b〉in the triangulation and replaces it with a new vertex c
    (and modifies the triangulation around the vertex c). This operation is only allowed if the topological type of
    the surface is not altered by the modification. This can be checked by comparing the link of the the edge〈a, b〉
    and the links of the vertices a and b.

    Literature: Computational Topology, pages 52 - 57

    Data source: http://graphics.stanford.edu/data/3Dscanrep/
"""


def edge_contraction(graph, edge):
    """ Edge contraction algorithm. """
    pass


def deformation_error(graph, edge):
    """ Score that measures how deformed the graph becomes by contracting the edge. """
    pass


def sort_edges(triangulation):
    """ Sort edges in triangulation according to deformation to graph. """
    pass

