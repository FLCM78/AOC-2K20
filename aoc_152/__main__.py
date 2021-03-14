import sys
import tracing

def main():
    idx = 0
    current = None
    history = {}

    raw = sys.stdin.readline()


    for value in [int(r) for r in raw.split(",")]:
        if current is not None:
            history[current] = idx

        current = value
        idx += 1

    for _ in range(idx, 30000000):
        # tracing.info("idx: {:9d}, current: {:9d}, history: {:9d}", idx, current, len(history))
        if current in history:
            nxt = idx - history[current]
        else:
            nxt = 0

        history[current] = idx
        idx += 1
        current = nxt

    tracing.info("idx: {}, current: {}", idx, current, history)



if __name__ == "__main__":
    main()
