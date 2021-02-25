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
    responses = []
    response = set("abcdefghijklmnopqrstuvwxyz")

    for _raw in sys.stdin:
        raw = _raw.strip()

        if raw == "":
            tracing.info("new group: {}", response)
            responses.append(response)
            response = set("abcdefghijklmnopqrstuvwxyz")
            continue

        response &= set(raw)

    responses.append(response)

    result = sum(len(s) for s in responses)
    tracing.info("the result is: {}", result)


if __name__ == "__main__":
    main()
