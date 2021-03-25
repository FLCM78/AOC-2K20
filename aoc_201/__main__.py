from collections import defaultdict
import io
import re
import sys
import tracing

LTL_ENDIAN = "little"
BIG_ENDIAN = "big"

ENDIANNESSES = [LTL_ENDIAN, BIG_ENDIAN]

TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"

DIRECTIONS = [LEFT, TOP, RIGHT, BOTTOM]

class Signature:
    def __init__(self, tile_idx, direction, key):
        self.tile_idx = tile_idx
        self.key = key
        self.direction = direction

    @classmethod
    def compute(cls, iterator):
        big, ltl = 0, 0

        for i, test in enumerate(iterator):
            big <<= 1
            if test is True:
                big += 1
                ltl += (1 << i)

        return min(ltl, big)

class TileSignature(dict):
    def __init__(self, tile_idx):
        self.tile_idx = tile_idx

    def __str__(self):
        buf = io.StringIO()
        buf.write(f"tile[{self.tile_idx}] = {{")

        for i in DIRECTIONS:
            if i != DIRECTIONS[0]:
                buf.write(", ")
            buf.write(f"{i}: {self[i].key}")

        buf.write("}")

        return buf.getvalue()

    @classmethod
    def compute(cls, tile):
        sign = TileSignature(tile.idx)

        for direction, j in [("left", 0), ("right", tile.size - 1)]:
            key = Signature.compute(
                tile.get(i, j) == "#" for i in range(tile.size)
            )
            sign[direction] = Signature(tile.idx, direction, key)

        for direction, i in [("top", 0), ("bottom", tile.size - 1)]:
            key = Signature.compute(
                tile.get(i, j) == "#" for j in range(tile.size)
            )
            sign[direction] = Signature(tile.idx, direction, key)

        return sign

class Tile:
    Tiles = {}

    @classmethod
    def register(cls, tile):
        assert tile.idx not in cls.Tiles

        cls.Tiles[tile.idx] = tile

    def __init__(self, idx, size, payload):
        self.idx = idx
        self.size = size
        self.payload = payload
        self.signature = TileSignature.compute(self)
        self.register(self)

        assert (size  ** 2) == len(payload)

    def get(self, i, j):
        return self.payload[i * self.size + j]

    def pprint(self):
        buf = io.StringIO()

        buf.write("┌")
        for k in range(self.size):
            if k > 0:
                buf.write("┬")
            buf.write("───")
        buf.write("┐")
        buf.write("\n")

        for i in range(self.size):
            if i > 0:
                buf.write("├")
                for k in range(self.size):
                    if k > 0:
                        buf.write("┼")
                    buf.write("───")
                buf.write("┤")
                buf.write("\n")

            for j in range(self.size):
                buf.write("│")
                col = 2 if self.get(i, j) == "#" else 0
                buf.write(f"\033[3{col}m a \033[0m")

            buf.write("│\n")

        buf.write("└")
        for k in range(self.size):
            if k > 0:
                buf.write("┴")
            buf.write("───")
        buf.write("┘")

        return buf.getvalue()

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

def main():
    for head in sys.stdin:
        Tile.parse(head)

    tracing.info("nb tiles: {}", len(Tile.Tiles))

    sign_idx = defaultdict(dict)
    for tile in Tile.Tiles.values():
        for sign in tile.signature.values():
            sign_idx[sign.key][sign.tile_idx] = sign

    corners = []
    for tile in Tile.Tiles.values():
        tracing.info("tile {} - signature {}", tile.idx, tile.signature)

        neighbors = {}
        for direction in DIRECTIONS:
            key = tile.signature[direction].key

            for tile_idx, sign in sign_idx[key].items():
                if tile.idx == tile_idx:
                    continue

                assert direction not in neighbors
                neighbors[direction] = sign.tile_idx

            if direction in neighbors:
                tracing.info("tile {} [{}]: {}", tile.idx, direction, neighbors[direction])

        tile.neighbors = neighbors

        assert len(neighbors) >= 2
        if len(neighbors) == 2:
            corners.append(tile)

    res = 1
    for tile in corners:
        res *= tile.idx
        tracing.info("corner {} - {}", tile.idx, tile.neighbors)

    tracing.info("res {}", res)

if __name__ == "__main__":
    main()
