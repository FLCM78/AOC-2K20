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
                return True

        return False

    @classmethod
    def from_string(cls, cstr_str):
        slices = [Slice.from_string(s) for s in cstr_str.split("or")]
        return cls(slices)


class Headers:
    """ Headers """

    def __init__(self, headers):
        self.headers = headers

    @classmethod
    def _pp_options(cls, options, msg=None):
        tracing.debug("---- START OPTIONS ---- {}", msg if msg else "")
        for idx, values in enumerate(options):
            tracing.debug("column[{}] can be {}", idx, ", ".join(values))
        tracing.debug("---- END OPTIONS ----")

    def is_valid(self, ticket):
        for idx, value in enumerate(ticket):
            for header in self.headers.values():
                if header.validate(value):
                    break
            else:
                tracing.info("tickect[{}] = {} is not valid", idx,  value)
                return False

        return True

    def _eliminate(self, options, column_idx, name):
        if name not in options[column_idx]:
            return

        options[column_idx].remove(name)

        assert len(options) > 0

        if len(options[column_idx]) == 1:
            (header_name, ) = options[column_idx]
            tracing.info(" column {} is '{}'" , column_idx, header_name)

            for idx, option in enumerate(options):
                if idx != column_idx and header_name in option:
                    tracing.debug("remove '{}' from column {}" , header_name, idx)
                    self._eliminate(options, idx, header_name)

    def _resolve(self, options, ticket):
        assert len(ticket) == len(self.headers)

        self._pp_options(options, "cheking new ticket with startup")

        for idx, value in enumerate(ticket):
            for header, constraint in self.headers.items():
                if header not in options[idx]:
                    continue

                if not constraint.validate(value):
                    tracing.debug("[{}] value {} doesn't match {} => column {} can't be {}",
                                  idx, value, header, idx, header)
                    self._eliminate(options, idx, header)

    def resolve(self, tickets):
        options = [set(self.headers.keys()) for _ in range(len(self.headers))]

        for ticket_idx, ticket in enumerate(tickets):
            if not self.is_valid(ticket):
                tracing.info("ticket[{}] is not valid: ignore", ticket_idx)
                continue

            tracing.error("using ticket[{}] = {}", ticket_idx, ticket)
            self._resolve(options, ticket)

        self._pp_options(options)

        names = []
        for idx, opts in enumerate(options):
            (name,) = opts
            tracing.info("column[{}] = '{}'", idx, name)
            names.append(name)

        return names

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

    return Headers(headers), tickets

def main():
    headers, tickets = parse()
    names = headers.resolve(tickets)

    res = 1
    for idx, name in enumerate(names):
        if not name.startswith("departure "):
            continue

        res *= tickets[0][idx]

    tracing.info("result: {}", res)

if __name__ == "__main__":
    main()
