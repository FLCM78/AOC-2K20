import sys
import tracing

def main():
    count = 0
    nb_cols = None

    for idx, _raw in enumerate(sys.stdin):
        raw = _raw.strip()

        if nb_cols:
            assert len(raw) == nb_cols, f"number of cols at {idx + 1}: {nb_cols} != {len(raw)}"
        else:
            nb_cols = len(raw)

        if raw[3 * idx % nb_cols] == "#":
            count += 1

    tracing.info("Number of matching passwords {count}", count=count)

if __name__ == "__main__":
    main()
