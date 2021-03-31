import sys

class Point2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point2D(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def neighbors(self):
        yield self + Point2D(1, 0)
        yield self + Point2D(0, 1)
        yield self + Point2D(-1, 1)
        yield self + Point2D(-1, 0)
        yield self + Point2D(0, -1)
        yield self + Point2D(1, -1)


def read_point(data):
    pos = 0
    point = Point2D()

    while pos < len(data):
        if data[pos] == "e":
            point += Point2D(1, 0)
            pos += 1
            continue

        if data[pos] == "w":
            point += Point2D(-1, 0)
            pos += 1
            continue

        if data[pos] == "s":
            pos += 1
            if data[pos] == "e":
                point += Point2D(1, -1)
            else:
                assert data[pos] == "w"
                point += Point2D(0, -1)

            pos +=1
            continue

        if data[pos] == "n":
            pos += 1
            if data[pos] == "e":
                point += Point2D(0, 1)
            else:
                assert data[pos] == "w"
                point += Point2D(-1, 1)

            pos +=1
            continue

    print(point)
    return point

def main():
    blacks = set()

    for _raw in sys.stdin:
        raw = _raw.strip()
        point = read_point(raw)

        if point in blacks:
            blacks.remove(point)
        else:
            blacks.add(point)


    for i in range(100):
        nxt_blacks = set()
        for black in blacks:
            cnt = 0
            for nbg in black.neighbors():
                if nbg in blacks:
                    cnt += 1

            if 1 <= cnt <= 2:
                nxt_blacks.add(black)

        print(len(nxt_blacks))

        neighbors = {}
        for black in blacks:
            for nbg in black.neighbors():
                if nbg in blacks:
                    continue

                if nbg not in neighbors:
                    neighbors[nbg] = { black }
                else:
                    neighbors[nbg].add(black)

        for pnt in neighbors:
            if len(neighbors[pnt]) == 2:
                nxt_blacks.add(pnt)

        print("Day", i, len(nxt_blacks))
        blacks = nxt_blacks



    # print("result:", len(blacks))

if __name__ == "__main__":
    main()
