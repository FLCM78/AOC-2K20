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
        return 0

class ValueNode(BaseNode):
    def __init__(self, value):
        self.value = value

    def match(self, string):
        if string.startswith(self.value):
            yield len(self.value)

class SeqNode(BaseNode):
    def __init__(self, *args):
        self.sequence = args

    def _match(self, string, seq):
        for skip in self.Tree[seq[0]].match(string):
            if len(seq) == 1:
                yield skip
            elif skip < len(string):
                for nxt in self._match(string[skip:], seq[1:]):
                    yield skip + nxt

    def match(self, string):
        return self._match(string, self.sequence)

class OrNode(BaseNode):
    def __init__(self, *args):
        self.choices = args

    def match(self, string):
        for choice in self.choices:
            for skip in choice.match(string):
                yield skip

def main():
    for raw in sys.stdin:
        if raw == "\n":
            break

        if raw[0] == "#":
            continue

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

    count = 0
    for _raw in sys.stdin:
        raw = _raw.strip()
        for skip in BaseNode.match(raw):
            if skip == len(raw):
                tracing.info("raw \"{}\" is a match", raw.strip())
                count += 1
                break
        else:
            tracing.error("raw \"{}\" is not a match", raw.strip())

    tracing.info("{} messages match rules 0", count)

if __name__ == "__main__":
    main()
