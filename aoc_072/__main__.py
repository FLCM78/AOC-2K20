import re
import sys
import tracing

COLORS = {}

def parse(_raw):
    raw = _raw.strip()
    parent_color, containers = raw[:-1].split(" bags contain ")

    if parent_color not in COLORS:
        COLORS[parent_color] = {}

    for container_raw in containers.split(", "):
        if container_raw == "no other bags":
            continue

        match = re.match(r"(?P<count>[0-9]+) (?P<color>.*) bags?", container_raw)
        assert match
        count = int(match.group("count"))
        color = match.group("color")

        COLORS[parent_color][color] = count

def count_colors(parent_color):
    if parent_color not in COLORS:
        return 0

    count = 0
    for color, color_count in COLORS[parent_color].items():
        count += color_count * (1 + count_colors(color))

    return count

def main():
    color = "shiny gold"

    for raw in sys.stdin:
        parse(raw)

    tracing.info("the result is: {}", count_colors(color))

if __name__ == "__main__":
    main()
