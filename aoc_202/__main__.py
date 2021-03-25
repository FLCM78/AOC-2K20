from collections import defaultdict
import io
import re
import sys
import tracing
from grid_2d import SquareGrid2d

LTL_ENDIAN = "little"
BIG_ENDIAN = "big"

ENDIANNESSES = [LTL_ENDIAN, BIG_ENDIAN]

TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"

DIRECTIONS = {
    RIGHT: 0,
    TOP: 1,
    LEFT: 2,
    BOTTOM: 3,
}

DIRECTIONS_NAMES = {
    0: RIGHT,
    1: TOP,
    2: LEFT,
    3: BOTTOM,
}

def compute_rotation(orig, dest):
    orig_idx = DIRECTIONS[orig]
    dest_idx = DIRECTIONS[dest]

    return (dest_idx - orig_idx) % 4

def lazy_sqrt(size):
    for i in range(size):
        if (i * i) == size:
            return i

        if (i * i) > size:
            break

    raise ValueError(f"{size} is not a magic number")

class Signature:
    def __init__(self, tile_idx, direction, key, endianness):
        self.tile_idx = tile_idx
        self.direction = direction
        self.key = key
        self.endianness = endianness

    def __str__(self):
        return f"{self.key} [{self.endianness}]"

    def __eq__(self, other):
        return self.endianness == other.endianness and self.key == other.key

    @classmethod
    def compute(cls, iterator):
        big, ltl = 0, 0

        for i, test in enumerate(iterator):
            big <<= 1
            if test is True:
                big += 1
                ltl += (1 << i)

        assert ltl != big

        if ltl < big:
            return ltl, LTL_ENDIAN

        return big, BIG_ENDIAN

class TileSignature(dict):
    def __init__(self, tile_idx):
        super().__init__()
        self.tile_idx = tile_idx

    def __str__(self):
        buf = io.StringIO()
        buf.write(f"tile[{self.tile_idx}] = {{")

        first = True
        for i in DIRECTIONS:
            if not first:
                buf.write(", ")
            buf.write(f"{i}: {self[i]}")
            first = False

        buf.write("}")

        return buf.getvalue()

    @classmethod
    def compute(cls, tile):
        sign = TileSignature(tile.idx)

        key, endianness = Signature.compute(
            tile.get(i, 0) == "#" for i in range(tile.size)
        )
        sign[LEFT] = Signature(tile.idx, LEFT, key, endianness)

        key, endianness = Signature.compute(
            tile.get(i, tile.size - 1) == "#" for i in range(tile.size)
        )
        sign[RIGHT] = Signature(tile.idx, RIGHT, key, endianness)

        key, endianness = Signature.compute(
            tile.get(0, j) == "#" for j in range(tile.size)
        )
        sign[TOP] = Signature(tile.idx, TOP, key, endianness)

        key, endianness = Signature.compute(
            tile.get(tile.size - 1, j) == "#" for j in range(tile.size)
        )
        sign[BOTTOM] = Signature(tile.idx, BOTTOM, key, endianness)

        return sign

class Grid(SquareGrid2d):
    PATTERN_SIZE = (3, 20)
    PATTERN = [
        (0, 18),
        (1, 0), (1, 5), (1, 6), (1, 11), (1, 12), (1, 17), (1, 18), (1, 19),
        (2, 1), (2, 4), (2, 7), (2, 10), (2, 13), (2, 16)
    ]

    def __init__(self, size, payload):
        super().__init__(size, payload)
        self.cur =  (0, 0)
        self.matches = set()

    def search_pattern(self):
        for idx in range(self.size):
            if idx + self.PATTERN_SIZE[0] > self.size:
                break

            for jdx in range(self.size):
                if jdx + self.PATTERN_SIZE[1] > self.size:
                    break

                self.cur = (idx, jdx)
                # tracing.info("\n{}", self.pprint())

                for pos in self.PATTERN:
                    i, j = self.cur[0] + pos[0], self.cur[1] + pos[1]
                    assert 0 <= i < self.size
                    assert 0 <= j < self.size
                    if self.get(i, j) != "#":
                        break
                else:
                    tracing.info("match at {}", self.cur)
                    matches = set((self.cur[0] + p[0], self.cur[1] + p[1]) for p in self.PATTERN)
                    self.matches |= matches

    def pp_item(self, i, j, item):
        if (i, j) in self.matches:
            return f"\033[48;5;10m {item} \033[0m"
        return f" {item} "

class Tile(SquareGrid2d):
    Tiles = {}

    @classmethod
    def register(cls, tile):
        assert tile.idx not in cls.Tiles
        cls.Tiles[tile.idx] = tile

    def __init__(self, idx, size, payload):
        super().__init__(size, payload)
        self.idx = idx
        self.neighbors = {}
        self.signature = TileSignature.compute(self)
        self.register(self)

    def rotate(self, nb_pi_2):
        super().rotate(nb_pi_2)
        self.signature = TileSignature.compute(self)

        neighbors = {}
        for i, nbg in self.neighbors.items():
            i = DIRECTIONS_NAMES[(DIRECTIONS[i] + nb_pi_2) % 4]
            neighbors[i] = nbg

        self.neighbors = neighbors

    def flip_v(self):
        super().flip_v()
        self.signature = TileSignature.compute(self)

        neighbors = {}
        for direction, nbg in self.neighbors.items():
            if direction == RIGHT:
                neighbors[LEFT] = nbg
            elif direction == LEFT:
                neighbors[RIGHT] = nbg
            else:
                neighbors[direction] = nbg

        self.neighbors = neighbors

    def flip_h(self):
        super().flip_h()
        self.signature = TileSignature.compute(self)

        neighbors = {}
        for direction, nbg in self.neighbors.items():
            if direction == TOP:
                neighbors[BOTTOM] = nbg
            elif direction == BOTTOM:
                neighbors[TOP] = nbg
            else:
                neighbors[direction] = nbg

        self.neighbors = neighbors

    def pp_item(self, i, j, item):
        col = 2 if item == "#" else 0
        return f"\033[3{col};48;5;{col + 8}m {self.hash(i,j)}\033[0m"

    @classmethod
    def compute_neighbors(cls):
        sign_idx = defaultdict(dict)
        for tile in cls.Tiles.values():
            for sign in tile.signature.values():
                sign_idx[sign.key][sign.tile_idx] = sign

        corners = []
        for tile in Tile.Tiles.values():
            # tracing.info("tile {} - signature {}", tile.idx, tile.signature)

            neighbors = {}
            for direction in DIRECTIONS:
                key = tile.signature[direction].key

                for tile_idx, sign in sign_idx[key].items():
                    if tile.idx == tile_idx:
                        continue

                    assert direction not in neighbors
                    neighbors[direction] = sign.tile_idx

            assert len(neighbors) >= 2
            if len(neighbors) == 2:
                corners.append(tile)

            tile.neighbors = neighbors

        return corners

    @classmethod
    def assemble_init(cls, corners):
        start = None
        for tile in corners:
            if "bottom" in tile.neighbors and "right" in tile.neighbors:
                start = tile
                break
        else:
            assert False, "missing start"

        size = lazy_sqrt(len(Tile.Tiles))
        tracing.info("big grid size is {}x{}", size, size)
        elements = [[None] * size for _ in range(size)]
        elements[0][0] = start

        return elements

    @classmethod
    def next_element(cls, cur, cur_dir):
        nxt = Tile.Tiles[cur.neighbors[cur_dir]]
        nxt_dir = DIRECTIONS_NAMES[(DIRECTIONS[cur_dir] + 2) % 4]

        for sign in nxt.signature.values():
            if sign.key == cur.signature[cur_dir].key:
                rot = compute_rotation(sign.direction, nxt_dir)
                if rot > 0:
                    nxt.rotate(rot)
                break

        if cur.signature[cur_dir].endianness != nxt.signature[nxt_dir].endianness:
            if cur_dir in [TOP, BOTTOM]:
                nxt.flip_v()
            else:
                nxt.flip_h()

        assert cur.signature[cur_dir] == nxt.signature[nxt_dir]

        return nxt

    @classmethod
    def assemble(cls, elements):
        size = len(elements)
        tile_size = elements[0][0].size

        for j in range(size):
            for i in range(size):
                # tracing.info("\n{}", pp_grid(elements, elements[0][0].size))
                cur = elements[i][j]
                assert isinstance(cur, Tile), f"{i}, {j} = {cur}"

                if i == 0:
                    assert TOP not in cur.neighbors

                if i == (size - 1):
                    assert BOTTOM not in cur.neighbors
                    continue

                if j == 0:
                    assert LEFT not in cur.neighbors
                else:
                    assert LEFT in cur.neighbors
                    assert elements[i][j - 1].idx == cur.neighbors[LEFT]
                    assert elements[i][j - 1].signature[RIGHT] == cur.signature[LEFT]

                if j  == (size - 1):
                    assert RIGHT not in cur.neighbors

                assert BOTTOM in cur.neighbors
                assert elements[i + 1][j] is None
                elements[i + 1][j] = cls.next_element(cur, BOTTOM)

            if j == (size - 1):
                break

            cur = elements[0][j]
            assert isinstance(cur, Tile), f"0, {j} = {cur}"
            assert RIGHT in cur.neighbors
            assert elements[0][j + 1] is None

            nxt = cls.next_element(cur, RIGHT)
            elements[0][j + 1] = nxt

        grid_size = len(elements) * (tile_size - 2)

        buf = io.StringIO()
        for raw in elements:
            for idx in range(1, tile_size - 1):
                for tile in raw:
                    for jdx in range(1, tile_size - 1):
                        buf.write(tile.get(idx, jdx))

        return Grid(grid_size, buf.getvalue())


    @classmethod
    def parse(cls, head):
        match = re.match(r"Tile ([\d]+):\n", head)
        assert match

        idx = int(match.group(1))
        nb_raws = 0
        nb_cols = None
        payload = io.StringIO()

        for _raw in sys.stdin:
            if _raw == "\n":
                break

            raw = _raw.strip()
            if nb_cols is None:
                nb_cols = len(raw)
            else:
                assert nb_cols == len(raw)

            nb_raws += 1
            payload.write(raw)

        assert nb_cols == nb_raws

        return cls(idx, nb_raws, payload.getvalue())

def pp_grid(elements, tile_size):
    buf = io.StringIO()

    for idx, raw in enumerate(elements):
        if idx > 0:
            buf.write("\n")

        for _ in raw:
            buf.write(Tile.pp_hup(tile_size))
        buf.write("\n")

        for i in range(tile_size):
            if i > 0:
                for _ in raw:
                    buf.write(Tile.pp_sep(tile_size))
                buf.write("\n")

            for tile in raw:
                if tile is not None:
                    assert tile.size == tile_size
                    buf.write(tile.pp_raw(i))
                else:
                    buf.write(Tile.pp_empty(tile_size))
            buf.write("\n")


        for _ in raw:
            buf.write(Tile.pp_hbt(tile_size))

    return buf.getvalue()

def main():
    for head in sys.stdin:
        Tile.parse(head)

    corners = Tile.compute_neighbors()
    elements = Tile.assemble_init(corners)
    grid = Tile.assemble(elements)
    tracing.info("\n{}", grid.pprint())

    actions = [
        lambda: 0,
        lambda: grid.rotate(1),
        lambda: grid.rotate(1),
        lambda: grid.rotate(1),
        lambda: grid.flip_v(),
        lambda: grid.rotate(1),
        lambda: grid.rotate(1),
        lambda: grid.rotate(1),
    ]

    for action in actions:
        action()
        grid.search_pattern()
        if len(grid.matches) > 0:
            break
    else:
        tracing.error("not found")

    tracing.info("\n{}", grid.pprint())

    count = 0
    for i in range(grid.size):
        for j in range(grid.size):
            if grid.get(i, j) == "#" and (i, j) not in grid.matches:
                count += 1

    tracing.info("count: {}", count)


if __name__ == "__main__":
    main()
