import sys
import tracing

def get_pos(_raw):
    raw = _raw.strip()

    assert len(raw) == 10

    row = 0
    for x in raw[:7]:
        row = (1 if x == "B" else 0) + (row << 1)
        tracing.info("row: {}", row)

    col = 0
    for x in raw[7:]:
        col = (1 if x == "R" else 0) + (col << 1)

    return row * 8 + col


def main():
    ids = [get_pos(r) for r in sys.stdin]
    ids.sort()

    for idx in range(len(ids) - 1):
        if (ids[idx + 1] - ids[idx]) == 2:
            tracing.info("my position {}", ids[idx] + 1)



if __name__ == "__main__":
    main()
