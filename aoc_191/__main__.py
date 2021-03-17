import re
import sys
import tracing

class BaseNode:
    Tree = {}

    @classmethod
    def match(cls, string):
        return cls.Tree[0].match(string)

    @classmethod
    def consume(cls):
        return cls.Tree[0].consume()

class ValueNode(BaseNode):
    def __init__(self, value):
        self.value = value

    @classmethod
    def consume(cls):
        return 1

    def match(self, string):
        return string.startswith(self.value)

class SeqNode(BaseNode):
    def __init__(self, *args):
        self.children = args
        self._consume = None

    def consume(self):
        if self._consume is None:
            consume = 0
            for child in self.children:
                consume += self.Tree[child].consume()

            self._consume = consume

        return self._consume

    def match(self, string):
        for child in self.children:
            if not self.Tree[child].match(string):
                return False

            string = string[self.Tree[child].consume():]

        return True

class OrNode(BaseNode):
    def __init__(self, *args):
        self.choices = args
        self._consume = None

    def consume(self):
        if self._consume is None:
            for choice in self.choices:
                cons = choice.consume()
                if self._consume is None:
                    self._consume = cons
                else:
                    assert self._consume == cons

        return self._consume

    def match(self, string):
        for choice in self.choices:
            if choice.match(string):
                return True

        return False

def main():
    for raw in sys.stdin:
        if raw == "\n":
            break

        idx, rule = raw.strip().split(":")
        idx = int(idx)
        tracing.info("{}: {}", idx, rule)

        match = re.match(r"^\s*\"([a-zA-Z])\"\s*$", rule)
        if match:
            BaseNode.Tree[idx] = ValueNode(match.group(1))
            continue

        nodes = []
        for item in rule.split("|"):
            elements = [int(e) for e in item.strip().split()]
            nodes.append(SeqNode(*elements))

        BaseNode.Tree[idx] = OrNode(*nodes)

    for idx, node in BaseNode.Tree.items():
        tracing.info("node {} consumes {}", idx, node.consume())

    count = 0
    for _raw in sys.stdin:
        raw = _raw.strip()
        if BaseNode.match(raw) and len(raw) == BaseNode.consume():
            tracing.info("raw \"{}\" is a match", raw.strip())
            count += 1
        else:
            tracing.error("raw \"{}\" is not a match", raw.strip())

    tracing.info("{} messages match rules 0", count)

if __name__ == "__main__":
    main()
