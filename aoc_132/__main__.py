import sys
import tracing

def main():
    _ = sys.stdin.readline()
    raw = sys.stdin.readline().strip().split(",")

    step = 1
    timestamp = 0

    for offset, item in enumerate(raw):
        if item == "x":
            continue

        bus_id = int(item)
        tracing.info("bus_id: {}, offset: {}", bus_id, offset)

        while (timestamp + offset) % bus_id != 0:
            timestamp += step

        step *= bus_id

        tracing.info("t + {} = {} * k => {}", offset, bus_id, timestamp)

if __name__ == "__main__":
    main()
