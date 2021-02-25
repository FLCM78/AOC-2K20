import sys
import tracing

SLOPES = {
 (1, 1): 0,
 (3, 1): 0,
 (5, 1): 0,
 (7, 1): 0,
 (1, 2): 0,

}

def main():
    count = 0
    nb_cols = None

    for idx, _raw in enumerate(sys.stdin):
        raw = _raw.strip()

        if nb_cols:
            assert len(raw) == nb_cols, f"number of cols at {idx + 1}: {nb_cols} != {len(raw)}"
        else:
            nb_cols = len(raw)


        for slope in SLOPES:
            if idx % slope[1]:
                continue

            pos = slope[0] * (idx // slope[1]) % nb_cols

            if raw[pos] == "#":
                SLOPES[slope] += 1

    res = 1
    for slope, count in SLOPES.items():
        tracing.info(f"SLOPE {slope}: {count}")
        res *= count

    tracing.info(f"Total {res}")

if __name__ == "__main__":
    main()
