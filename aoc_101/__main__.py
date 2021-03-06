from collections import defaultdict as ddict
import sys
import tracing


def main():
    jumps = ddict(int)
    stack = [int(r) for r in sys.stdin]
    stack.sort()

    for i, cnt in enumerate(stack):

        if i > 0:
            cnt -= stack[i - 1]

        jumps[cnt] += 1

    for jmp, cnt in jumps.items():
        tracing.info("Jump: {}, Count: {}", jmp, cnt)

    res = jumps[1] * (jumps[3] + 1)
    tracing.info("Result: {}", res)

if __name__ == "__main__":
    main()
