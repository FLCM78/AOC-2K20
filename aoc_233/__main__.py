import io

NB_CUPS = 1000000
NB_ROUNDS = 10000000
HASH = [(i + 1) % NB_CUPS for i in range(NB_CUPS)]

def init_hash(*args):
    for idx, arg in enumerate(args):
        if idx == 0:
            prev = args[-1] if len(args) == NB_CUPS else (NB_CUPS - 1)
        else:
            prev = args[idx - 1]

        HASH[prev] = arg

    if len(args) < NB_CUPS:
        HASH[args[-1]] = len(args)

    return args[0]

def play(cur):
    one = HASH[cur]
    two = HASH[one]
    three = HASH[two]

    HASH[cur] = HASH[three]

    nxt = cur
    while True:
        nxt = nxt - 1 if nxt > 0 else NB_CUPS - 1
        if nxt not in [one, two, three]:
            break

    HASH[three] = HASH[nxt]
    HASH[nxt] = one

    return HASH[cur]

def pp_hash(cur):
    buf = io.StringIO()

    buf.write("{")
    for idx in range(NB_CUPS + 1):
        if idx != 0:
            buf.write(", ")
        buf.write(str(cur + 1))
        cur = HASH[cur]

    buf.write("}")

    return buf.getvalue()

def main():
    raw = "916438275"
    raw = "389125467"

    print(f"init with '{raw}'")
    cur = init_hash(*(int(r) - 1 for r in raw))

    # print(pp_hash(cur))

    for i in range(NB_ROUNDS):
        if ((i + 1) % 1000) == 0:
            print("round ", i + 1, end="\r")
        cur = play(cur)

    # print("final:", pp_hash(cur))
    print("")
    print("one fater 1:", HASH[0] + 1)
    print("two after 1:", HASH[HASH[0]] + 1)
    print("result:", (HASH[0] + 1) * (HASH[HASH[0]] + 1))

if __name__ == "__main__":
    main()
