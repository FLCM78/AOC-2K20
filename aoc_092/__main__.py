import sys
import tracing

PREAMBLE_SZ = 25

def check_stack(stack, pos):
    for i in range(PREAMBLE_SZ):
        pos_i = pos - PREAMBLE_SZ + i

        for j in range(i, PREAMBLE_SZ):
            if j == i:
                continue

            pos_j = pos - PREAMBLE_SZ + j
            allowed = stack[pos_i] + stack[pos_j]

            if allowed == stack[pos]:
                return True

    return False

def main():
    stack = [int(r) for r in sys.stdin]

    for pos in range(PREAMBLE_SZ, len(stack)):
        if not check_stack(stack, pos):
            key = stack[pos]
            break

    tracing.info("key: {}", key)

    for i in range(len(stack)):
        total = 0

        for j in range(i, len(stack)):
            total += stack[j]

            if total == key:
                tracing.info("bingo - [{}, {}]", i, j)
                smallest, largest = min(stack[i:j]), max(stack[i:j])
                tracing.info("smallest: {}, largest: {}", smallest, largest)
                tracing.info("result: {}", smallest + largest)
                return

            if total > key:
                break

if __name__ == "__main__":
    main()
