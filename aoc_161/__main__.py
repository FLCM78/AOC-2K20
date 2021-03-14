import sys
import tracing



class Slice:
    """ Store range """
    def __init__(self, beg, end):
        self.beg = beg
        self.end = end

    def __contains__(self, value):
        return self.beg <= value <= self.end

    def __str__(self):
        return f"[{self.beg}, {self.end}]"

    @classmethod
    def from_string(cls, slice_str):
        bounds = [int(s) for s in slice_str.split("-")]
        return cls(*bounds)

class Constraint:
    """ Column constraints """
    def __init__(self, slices):
        self.slices = slices

    def __str__(self):
        return "(" + " u ".join(str(s) for s in self.slices) + ")"

    def validate(self, value):
        for slc in self.slices:
            if value in slc:
                tracing.debug("validate {} in {} => True", value, self)
                return True

        tracing.debug("validate {} in {} => False", value, self)
        return False

    @classmethod
    def from_string(cls, cstr_str):
        slices = [Slice.from_string(s) for s in cstr_str.split("or")]
        return cls(slices)

def parse():
    headers = {}
    tickets = []

    tracing.info("reading headers")
    for _raw in sys.stdin:
        raw = _raw.strip()
        tracing.debug("line: '{}'", raw)
        if raw == "":
            break

        name, constraints = raw.split(":")
        tracing.debug("name: {}, constraint: {}", name, constraints)
        headers[name] = Constraint.from_string(constraints)
        tracing.debug("{}: {}", name, headers[name])

    tracing.info("reading my ticket")

    raw = sys.stdin.readline().strip()
    tracing.debug("line: '{}'", raw)
    assert raw == "your ticket:"

    raw = sys.stdin.readline().strip()
    tracing.debug("line: '{}'", raw)
    tickets.append([int(r) for r in raw.split(",")])

    tracing.info("my ticket: {}", tickets[0])

    raw = sys.stdin.readline().strip()
    tracing.debug("line: '{}'", raw)
    assert raw == ""

    tracing.info("reading nearby tickets")
    raw = sys.stdin.readline().strip()
    tracing.info("line: '{}'", raw)
    assert raw == "nearby tickets:"

    for _raw in sys.stdin:
        raw = _raw.strip()
        tracing.debug("line: '{}'", raw)
        tickets.append([int(r) for r in raw.split(",")])

    return headers, tickets

def main():
    headers, tickets = parse()
    res = 0

    for ticket in tickets[1:]:
        tracing.debug("ticket: {}", ticket)

        for idx, value in enumerate(ticket):
            tracing.debug("ticket[{}] = {}", idx, value)

            for header in headers.values():
                if header.validate(value):
                    break
            else:
                tracing.info("value {} is not valid", value)
                res += value

    tracing.info("res: {}", res)

if __name__ == "__main__":
    main()
