import sys
import tracing

from aoc_121.point import Point

class Boat:
    """ lala """

    North = Point(0, 1)
    South = Point(0, -1)
    East = Point(1, 0)
    West = Point(-1, 0)

    Actions = {}

    def __init__(self):
        self.position = Point()
        self.direction = Point(10, 1)

    def process(self, act, val):
        self.Actions[act](self, val)

    @classmethod
    def action(cls, code):
        def decorated(func):
            cls.Actions[code] = func
            return func

        return decorated

@Boat.action("N")
def go_north(boat, value):
    tracing.info("going north '{}'", value)
    boat.direction += value * Boat.North

@Boat.action("S")
def go_south(boat, value):
    tracing.info("going south '{}'", value)
    boat.direction += value * boat.South

@Boat.action("E")
def go_east(boat, value):
    tracing.info("going east '{}'", value)
    boat.direction += value * boat.East

@Boat.action("W")
def go_west(boat, value):
    tracing.info("going west '{}'", value)
    boat.direction += value * boat.West

@Boat.action("F")
def forward(boat, value):
    tracing.info("going forward '{}'", value)
    boat.position += value * boat.direction

@Boat.action("R")
def rotate_neg(boat, value):
    tracing.info("rotate neg '{}'", value)
    boat.direction = boat.direction.rotate(-value)

@Boat.action("L")
def rotate_pos(boat, value):
    tracing.info("rotate pos '{}'", value)
    boat.direction = boat.direction.rotate(value)

def main():
    boat = Boat()

    for raw in sys.stdin:
        act = raw[0]
        val = int(raw[1:])

        tracing.info("processing action '{}' ({})", act, val)
        boat.process(act, val)

    tracing.info("Boat position is {}", boat.position)

if __name__ == "__main__":
    main()
