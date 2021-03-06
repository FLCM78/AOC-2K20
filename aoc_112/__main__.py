import io
import sys
import tracing

class GridNode:
    """ Grid Element """

    def __init__(self, grid, raw, col):
        self.raw = raw
        self.col = col
        self.grid = grid

    def is_empty(self):
        return self.grid.is_empty(self.raw, self.col)

    def is_occupied(self):
        return self.grid.is_occupied(self.raw, self.col)

    def get_neighbor(self, draw, dcol):
        raw = self.raw
        col = self.col

        while True:
            raw += draw
            col += dcol

            if raw >= self.grid.nb_raws or raw < 0:
                return None

            if col >= self.grid.nb_cols or col < 0:
                return None

            if self.grid.is_seat(raw, col):
                return self.__class__(self.grid, raw, col)

    def neighbors(self):
        for direction in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)):
            nghb = self.get_neighbor(*direction)
            if nghb is not None:
                yield nghb

    def __str__(self):
        status = "occupied" if self.is_occupied() else "empty"
        return f"({self.raw}, {self.col}) [{status}]"

class Grid:
    """ Grid class """

    FLOOR_MRK = "."
    EMPTY_MRK = "L"

    def __init__(self, nb_raws, nb_cols, seats):
        self.nb_cols = nb_cols
        self.nb_raws = nb_raws

        self.generation = 0
        self.seats = [seats, None]


    def __iter__(self):
        for raw, col in self.seats[self.generation % 2]:
            yield GridNode(self, raw, col)

    def is_seat(self, raw, col):
        return (raw, col) in self.seats[self.generation % 2]

    def is_empty(self, raw, col):
        return self.seats[self.generation % 2][(raw, col)]

    def is_occupied(self, raw, col):
        return not self.is_empty(raw, col)

    def next_generation(self):
        nxt = {}
        mutation_cnt = 0

        for seat in self:
            cnt = 0
            for neighbor  in seat.neighbors():
                # tracing.info("{} -> {}", seat, neighbor)
                cnt += 1 if neighbor.is_occupied() else 0

            # tracing.info("Seat {} has {} occupied neigbors", seat, cnt)

            if cnt == 0 and seat.is_empty():
                # tracing.warn("Seat {} becomes occupied", seat)
                nxt[(seat.raw, seat.col)] = False
                mutation_cnt += 1
            elif cnt >= 5 and seat.is_occupied():
                # tracing.warn("Seat {} becomes empty", seat)
                nxt[(seat.raw, seat.col)] = True
                mutation_cnt += 1
            else:
                nxt[(seat.raw, seat.col)] = seat.is_empty()


        self.seats[(self.generation + 1) % 2] = nxt
        self.generation += 1

        return mutation_cnt

    @classmethod
    def from_file(cls, in_f):
        seats = {}

        for raw, _dsc in enumerate(in_f):
            dsc = _dsc.strip()

            for col, mrk in enumerate(dsc):
                if mrk == cls.FLOOR_MRK:
                    continue
                seats[(raw, col)] = mrk == cls.EMPTY_MRK

        return cls(raw + 1, col + 1, seats)

    def pprint(self):
        buf = io.StringIO()

        buf.write("┌")
        for k in range(self.nb_cols):
            if k > 0:
                buf.write("┬")
            buf.write("───")
        buf.write("┐")
        buf.write("\n")

        for i in range(self.nb_raws):
            if i > 0:
                buf.write("├")
                for k in range(self.nb_cols):
                    if k > 0:
                        buf.write("┼")
                    buf.write("───")
                buf.write("┤")
                buf.write("\n")

            for j in range(self.nb_cols):
                buf.write("│")
                if self.is_seat(i, j):
                    col = 2 if self.is_empty(i, j) else 1
                    buf.write(f"\033[3{col}m ✘ \033[0m")
                else:
                    col = 0
                    buf.write(f"\033[3{col}m   \033[0m")

            buf.write("│\n")

        buf.write("└")
        for k in range(self.nb_cols):
            if k > 0:
                buf.write("┴")
            buf.write("───")
        buf.write("┘")

        return buf.getvalue()


def main():
    grid = Grid.from_file(sys.stdin)
    tracing.info("The GRID:\n{}", grid.pprint())

    while grid.next_generation() > 0:
        # tracing.info("The GRID:\n{}", grid.pprint())
        tracing.info("generation {}", grid.generation)

    tracing.info("{} occupied seats", sum(1 if s.is_occupied() else 0 for s in grid))



if __name__ == "__main__":
    main()
