"""
    ~~~ Surface simplification - TDA project ~~~

    Implement an algorithm for simplifying surface triangulations by deleting superfluous edges.

"""

import data, helpers, edge_contraction

res = ["", "_res2", "_res3", "_res4"]

# testing read_data and plotting
in_file = "bunny/reconstruction/bun_zipper" + res[1] + ".ply"
points, triangulation = data.get_triangulation(in_file)

print("n triangles:", len(triangulation))
print("homology", helpers.homology(triangulation, points))

helpers.plot(triangulation, points)
graph = helpers.triangulation_to_graph(triangulation, points)

triangulation,points=edge_contraction.edge_contraction(graph,triangulation,points)
#data.save_ply("bunny/simplified/bun_zipper_2" + res[3] + ".ply", triangulation, points)
helpers.plot(triangulation, points)

print("n triangles:", len(triangulation))
print("homology", helpers.homology(triangulation, points))