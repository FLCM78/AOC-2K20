import re
import sys
import tracing

MASK_REGEX = re.compile(r"mask\s*=\s*(?P<mask>[X10]{36})\s*$")
MEM_REGEX = re.compile(r"mem\s*\[(?P<index>[0-9]+)\]\s*=\s*(?P<value>[0-9]+)\s*$")

def parse_mask(mask):
    tracing.info("found mask '{}'", mask)

    mask_on = 0
    mask_off = 0xffffffffffffffff

    for idx, item in enumerate(mask):
        if item == "1":
            mask_on |= 1 << (35 - idx)
        elif item == "0":
            mask_off &= ~(1 << (35 - idx))
        else:
            assert item == "X"

    tracing.info("mask_on: {}, mask_off: {}", mask_on, mask_off)

    return mask_on, mask_off

def main():
    memory = {}
    mask_on = 0
    mask_off = 0xffffffffffffffff

    for raw in sys.stdin:
        mask_match = MASK_REGEX.match(raw)
        if mask_match:
            mask_on, mask_off = parse_mask(mask_match.group("mask"))
            continue

        mem_match = MEM_REGEX.match(raw)
        if mem_match:
            index = int(mem_match.group("index"))
            value = int(mem_match.group("value"))
            tracing.info("set mem [{}] = {}", index, value)

            memory[index] = (value | mask_on) & mask_off
            continue

        raise RuntimeError(f"unexpected command '{raw.strip()}'")

    total = 0
    for item, value in memory.items():
        total += value
        tracing.info("mem [{}] = {}", item, value)

    tracing.info("total {}", total)


if __name__ == "__main__":
    main()
