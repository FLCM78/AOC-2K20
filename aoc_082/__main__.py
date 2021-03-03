import sys
import tracing

def run_code(code):
    idx = 0
    line = 0
    accum = 0
    stack = [[] for _ in range(len(code))]

    while 0 <= line < len(code):
        if len(stack[line]) == 1:
            tracing.error("ACCUM: {}", accum)
            return False

        idx += 1
        stack[line].append(idx)
        tracing.info("{:03d} | EXEC {} ", line, code[line])

        if code[line][0] == "nop":
            line += 1
        elif code[line][0] == "acc":
            accum += code[line][1]
            line += 1
        elif code[line][0] == "jmp":
            line += code[line][1]
        else:
            assert False

    tracing.info("ACCUM: {}", accum)
    return True


def main():
    code = []

    for raw in sys.stdin:
        cmd, val = raw.split()
        val = int(val)
        code.append([cmd, val])
        tracing.info("COMMAND: '{}', VALUE:'{}'", cmd, val)

    for idx, raw in enumerate(code):
        cmd, _ = raw

        if cmd == "nop":
            code[idx][0] = "jmp"
        elif cmd == "jmp":
            code[idx][0] = "nop"
        else:
            continue

        if run_code(code):
            return

        code[idx][0] = cmd

    # for idx, raw in enumerate(code):
    #     print("{:3d} | {} {:4d} | {}".format(idx, cmd, val, ", ".join(str(l) for l in lines)))

if __name__ == "__main__":
    main()
