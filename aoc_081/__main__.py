import sys
import tracing

COLORS = {}


def run_code(code):
    idx = 0
    line = 0
    accum = 0

    while 0 <= line < len(code):
        if len(code[line][2]) == 1:
            tracing.error("ACCUM: {}", accum)
            return

        idx += 1
        code[line][2].append(idx)
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


def main():
    code = []

    for raw in sys.stdin:
        cmd, val = raw.split()
        val = int(val)
        code.append([cmd, val, []])

        tracing.info("COMMAND: '{}', VALUE:'{}'", cmd, val)

    run_code(code)

    # for idx, raw in enumerate(code):
    #     cmd, val, lines = raw
    #     print("{:3d} | {} {:4d} | {}".format(idx, cmd, val, ", ".join(str(l) for l in lines)))

if __name__ == "__main__":
    main()
