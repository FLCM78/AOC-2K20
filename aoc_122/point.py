class Point:
    """ Base class for 2d algebra """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return self.__class__(scalar * self.x, scalar * self.y)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def rotate(self, angle):
        assert angle % 90 == 0
        mod_pi_2 = angle // 90

        if mod_pi_2 % 2:
            cos = 0
            sin = -1 if (mod_pi_2 // 2) % 2  else 1
        else:
            cos = -1 if (mod_pi_2 // 2) % 2 else 1
            sin = 0

        return self.__class__(cos * self.x - sin * self.y, sin * self.x + cos * self.y)
