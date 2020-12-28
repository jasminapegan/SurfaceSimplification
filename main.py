"""
    ~~~ Surface simplification - TDA project ~~~

    Implement an algorithm for simplifying surface triangulations by deleting superfluous edges.

"""

import read_data, helpers, edge_contraction

# testing read_data and plotting
in_file = "bunny/reconstruction/bun_zipper.ply"
points, triangulation = read_data.get_triangulation(in_file)


#helpers.plot(list(triangulation), points)

graph = helpers.triangulation_to_graph(triangulation, points)




