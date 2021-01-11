"""
    Read triangulation from a .ply file.
"""
from helpers import sorted_tuple


def get_triangulation(file):
    """ Returns list of points and list of triangle indices.
        Ex.: points = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
             triangulation = [(0, 1, 2)]
    """
    points = []
    triangulation = set()

    with open(file, "r") as f:

        # skip header
        line = f.readline()

        while line != "end_header\n":
            line = f.readline()

        for line in f.readlines():
            data = line.strip().split(" ")

            # lines of form x, y, z, and some data we don't need
            if len(data) == 5:
                points.append([float(x) for x in data[:3]])

            # lines of form 3, i, j, k (indices of points)
            elif len(data) == 4 and data[0] == '3':
                triangulation.add(sorted_tuple(*[int(i) for i in data[1:]]))

    return points, list(triangulation)

def export_ply(triangulation, points):
    triangulation = [t for t in triangulation
                     if len(t) == 3]
    data = """ply
format ascii 1.0           
comment Exported triangulation
comment 
element vertex {}
property float x
property float y
property float z
element face {}
property list uchar int vertex_index
end_header
""".format(len(points), len(triangulation))
    for point in points:
        data += " ".join(map(str, point)) + "\n"
    for simplex in triangulation:
        line = "{} ".format(len(simplex))
        line += " ".join(map(str, simplex))
        line += "\n"
        data += line
    return data


def save_ply(filename, triangulation, points):
    data = export_ply(triangulation, points)
    with open(filename, "w") as f:
        f.writelines(data)
