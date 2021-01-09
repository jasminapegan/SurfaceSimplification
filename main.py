"""
    ~~~ Surface simplification - TDA project ~~~

    Implement an algorithm for simplifying surface triangulations by deleting superfluous edges.

"""

import read_data, helpers, edge_contraction, networkx as nx

# testing read_data and plotting
#in_file = "bunny/reconstruction/test.ply"
in_file = "bunny/reconstruction/bun_zipper_res4.ply"
points, triangulation = read_data.get_triangulation(in_file)
print(len(triangulation))
print("homology", helpers.homology(triangulation))
helpers.plot(triangulation, points)
graph = helpers.triangulation_to_graph(triangulation, points)

triangulation,points=edge_contraction.edge_contraction(graph,triangulation,points)
helpers.plot(triangulation, points)

print(len(triangulation))
print("homology", helpers.homology(triangulation))