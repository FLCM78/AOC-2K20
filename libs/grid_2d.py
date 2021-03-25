import abc
import io

class Matrix:
    def __init__(self):
        self.array = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

    def __str__(self):
        buf = io.StringIO()

        for i in range(3):
            if i > 0:
                buf.write(", ")

            buf.write("[")
            buf.write(", ".join(f"{self.array[i][j]:2}" for j in range(3)))
            buf.write("]")

        return buf.getvalue()

    @classmethod
    def identity(cls):
        identity = cls()

        for i in range(3):
            identity.array[i][i] = 1

        return identity

    @classmethod
    def flip_h(cls):
        flip = cls()
        flip.array = [[-1, 0, 1], [0, 1, 0], [0, 0, 1]]
        return flip

    @classmethod
    def flip_v(cls):
        flip = cls()
        flip.array = [[1, 0, 0], [0, -1, 1], [0, 0, 1]]
        return flip

    @classmethod
    def rotate(cls):
        rot  = cls()
        rot.array = [[0, 1, 0], [-1, 0, 1], [0, 0, 1]]
        return rot

    def __mul__(self, other):
        mat = Matrix()

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    mat.array[i][j] += self.array[i][k] * other.array[k][j]

        return mat

    def transform(self, i, j, k):
        raw = self.array[0][0] * i + self.array[0][1] * j + self.array[0][2] * k
        col = self.array[1][0] * i + self.array[1][1] * j + self.array[1][2] * k

        # tracing.info("{}, {} => {}, {}", i, j, raw, col)
        return raw, col



class SquareGrid2d(abc.ABC):
    def __init__(self, size, payload):
        self.size = size
        self.payload = payload
        self.matrix = Matrix.identity()

        assert (size  ** 2) == len(payload)

    def get(self, i, j):
        return self.payload[self.hash(i, j)]

    def hash(self, i, j):
        i, j = self.matrix.transform(i, j, self.size - 1)

        return i * self.size + j

    def rotate(self, nb_pi_2):
        for _ in range(nb_pi_2):
            self.matrix *= self.matrix.rotate()

    def flip_v(self):
        self.matrix *= self.matrix.flip_v()

    def flip_h(self):
        self.matrix *= self.matrix.flip_h()

    @abc.abstractmethod
    def pp_item(self, i, j, item):
        pass

    @classmethod
    def pp_hup(cls, size):
        buf = io.StringIO()

        buf.write("┌")
        for k in range(size):
            if k > 0:
                buf.write("┬")
            buf.write("───")
        buf.write("┐")

        return buf.getvalue()

    @classmethod
    def pp_sep(cls, size):
        buf = io.StringIO()

        buf.write("├")
        for k in range(size):
            if k > 0:
                buf.write("┼")
            buf.write("───")
        buf.write("┤")

        return buf.getvalue()

    @classmethod
    def pp_hbt(cls, size):
        buf = io.StringIO()

        buf.write("└")
        for k in range(size):
            if k > 0:
                buf.write("┴")
            buf.write("───")
        buf.write("┘")

        return buf.getvalue()

    @classmethod
    def pp_empty(cls, tile_size):
        buf = io.StringIO()

        buf.write("│   " * tile_size)
        buf.write("│")

        return buf.getvalue()

    def pp_raw(self, i):
        buf = io.StringIO()

        for j in range(self.size):
            buf.write("│")
            buf.write(self.pp_item(i, j, self.get(i, j)))
        buf.write("│")

        return buf.getvalue()

    def pprint(self):
        buf = io.StringIO()

        buf.write(self.pp_hup(self.size))
        buf.write("\n")

        for i in range(self.size):
            if i > 0:
                buf.write(self.pp_sep(self.size))
                buf.write("\n")

            buf.write(self.pp_raw(i))
            buf.write("\n")

        buf.write(self.pp_hbt(self.size))

        return buf.getvalue()
