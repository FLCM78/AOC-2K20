import re
import sys
import tracing

class NodeTree:

    def __init__(self, color):
        self.color = color
        self.parents = {}

    def __getitem__(self, idx):
        return self.parents[idx]

    def __setitem__(self, idx, value):
        self.parents[idx] = value

COLORS = {}

def parse(_raw):
    raw = _raw.strip()
    parent_color, containers = raw[:-1].split(" bags contain ")

    if parent_color not in COLORS:
        COLORS[parent_color] = NodeTree(parent_color)

    for container_raw in containers.split(", "):
        if container_raw == "no other bags":
            continue

        match = re.match(r"(?P<count>[0-9]+) (?P<color>.*) bags?", container_raw)
        assert match
        count = int(match.group("count"))
        color = match.group("color")

        if color not in COLORS:
            COLORS[color] = NodeTree(color)

        COLORS[color][parent_color] = count

def count_colors(color):
    parents = set()

    for parent in COLORS[color].parents:
        parents.add(parent)

    tracing.info("{} can contain {}", parents, color)

    for parent in COLORS[color].parents:
        parents |= count_colors(parent)

    return parents

def main():
    color = "shiny gold"

    for raw in sys.stdin:
        parse(raw)

    tracing.info("the result is: {}", len(count_colors(color)))

if __name__ == "__main__":
    main()
