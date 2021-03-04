import sys
import tracing

PREAMBLE_SZ = 25

def check_stack(stack, pos):
    buff = stack[pos - PREAMBLE_SZ:pos]

    for i in range(PREAMBLE_SZ):
        pos_i = pos - PREAMBLE_SZ + i

        for j in range(i, PREAMBLE_SZ):
            if j == i:
                continue

            pos_j = pos - PREAMBLE_SZ + j
            allowed = stack[pos_i] + stack[pos_j]

            if allowed == stack[pos]:
                tracing.info("{:4d} | {} | allowed: {} + {}", pos, stack[pos], pos_i, pos_j)
                return True

    tracing.error("{:4d} | {} | not allowed !!", pos, stack[pos], pos_i, pos_j)
    return False

def main():
    stack = [int(r) for r in sys.stdin]

    for pos in range(PREAMBLE_SZ):
        tracing.info("{:4d} | {} | PREAMBLE", pos, stack[pos])

    for pos in range(PREAMBLE_SZ, len(stack)):
        check_stack(stack, pos)


if __name__ == "__main__":
    main()
