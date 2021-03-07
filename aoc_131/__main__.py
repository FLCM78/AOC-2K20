import sys
import tracing

def main():
    timestamp = int(sys.stdin.readline())

    raw = sys.stdin.readline().strip().split(",")

    min_wait = None
    min_bus_id = None

    tracing.info("timestamp {}", timestamp)

    for item in raw:
        if item == "x":
            continue

        bus_id = int(item)
        wait = timestamp % bus_id

        if wait != 0:
            wait = bus_id - wait

        tracing.info("wait {} for bus {}", wait, bus_id)
        if min_wait is None or wait < min_wait:
            min_wait = wait
            min_bus_id = bus_id

    tracing.info("min wait {} for bus {} ({})", min_wait, min_bus_id, min_wait * min_bus_id)

if __name__ == "__main__":
    main()
