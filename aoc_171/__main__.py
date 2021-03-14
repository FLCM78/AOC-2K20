import sys
import tracing

class IPoint3D:
    """ 3D Node """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def neighbors(self):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if i == 0 and j == 0 and k == 0:
                        continue
                    yield self.__class__(self.x + i, self.y + j, self.z + k)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"IPoint3d({self.x}, {self.y}, {self.z})"

class Grid:
    """ Grid class """

    EMPTY_MRK = "."
    POINT_MRK = "#"

    def __init__(self):
        self.points = {}

    def __contains__(self, point):
        return point in self.points

    @classmethod
    def from_file(cls, in_f):
        grid = cls()

        for y, _raw in enumerate(in_f):
            raw = _raw.strip()
            for x, mrk in enumerate(raw):
                if mrk == grid.EMPTY_MRK:
                    continue
                pos = IPoint3D(x, y, 0)
                grid.points[pos] = True

        return grid

def main():
    grid = Grid.from_file(sys.stdin)

    for _ in range(6):
        nxt_points = {}
        for pts in grid.points:
            cnt = 0

            for nbg in pts.neighbors():
                if nbg in grid:
                    cnt += 1

            if 2 <= cnt <= 3:
                nxt_points[pts] = True

        neighbors = {}
        for pnt in grid.points:
            for nbg in pnt.neighbors():
                if nbg in grid:
                    continue

                if nbg not in neighbors:
                    neighbors[nbg] = { pnt }
                else:
                    neighbors[nbg].add(pnt)

        for pnt in neighbors:
            if len(neighbors[pnt]) == 3:
                nxt_points[pnt] = True

        grid.points = nxt_points

    tracing.info("Number of active points: {}", len(grid.points))

if __name__ == "__main__":
    main()
