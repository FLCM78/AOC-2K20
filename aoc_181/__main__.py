import sys
import tracing


SUM_TKN = "+"
MUL_TKN = "*"
LFT_BRA = "("
RGT_BRA = ")"


OPERATORS = {
 "+": lambda x, y: x + y,
 "*": lambda x, y: x * y,
}

def parse_func(expr):
    idx = 0
    stack = []
    while idx < len(expr):

        if expr[idx] in [SUM_TKN, MUL_TKN, RGT_BRA, LFT_BRA]:
            stack.append(expr[idx])
            idx += 1
            continue

        if expr[idx].isspace():
            idx += 1
            continue

        if expr[idx].isdigit():
            value = 0
            while idx < len(expr) and expr[idx].isdigit():
                value = 10 * value + (ord(expr[idx]) - ord('0'))
                idx += 1
            stack.append(value)
            continue

        raise RuntimeError("Unexpected char at {}".format(idx))

    stack.reverse()
    return stack

def eval_func(stack, left=None, delim=None):
    tracing.info("stack: {}, left: {}", stack, left)

    if len(stack) == 0:
        if delim is not None:
            raise RuntimeError("Missing closing braket")

        return left

    nxt = stack.pop()
    if left is None:
        if isinstance(nxt, int):
            return eval_func(stack, left=nxt, delim=delim)

        if nxt == LFT_BRA:
            left = eval_func(stack, delim=RGT_BRA)
            return eval_func(stack, left=left, delim=delim)

        raise RuntimeError("Fuck 1")

    if nxt == RGT_BRA:
        if delim is None:
            raise RuntimeError("unexpected right bracket")

        return left

    if nxt in [SUM_TKN, MUL_TKN]:
        operator = nxt
        if len(stack) == 0:
            raise RuntimeError("missing right value after '{}'".format(operator))

        nxt = stack.pop()
        if isinstance(nxt, int):
            return eval_func(stack, left=OPERATORS[operator](left, nxt), delim=delim)

        if nxt == LFT_BRA:
            right = eval_func(stack, delim=RGT_BRA)
            return eval_func(stack, left=OPERATORS[operator](left, right), delim=delim)

        raise RuntimeError("Fuck 2")

def main():
    total = 0
    for idx, _raw in enumerate(sys.stdin):
        raw = _raw.strip()
        stack = parse_func(raw)
        res = eval_func(stack)
        total += res
        tracing.info("raw[{}] = '{}' => {}", idx, raw, stack)
        tracing.info("raw[{}] = '{}' => {}", idx, raw, res)

    tracing.info("total = {}", total)

if __name__ == "__main__":
    main()
