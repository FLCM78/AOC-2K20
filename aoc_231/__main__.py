import io

class Ring:
    NB_CUPS = 1000000

    def __init__(self, *args):
        self.items = list(args)
        for i in range(10, self.NB_CUPS + 1):
            self.items.append(i)


    def extract(self):
        tmp = self.items[1:4]
        self.items = self.items[:1] + self.items[4:]

        # tracing.info("RING: {}, tmp: {}", self, tmp)
        value = self.items[0] - 1
        index = None

        while index is None:
            if value < 1:
                value = self.NB_CUPS

            try:
                index = self.items.index(value)
            except ValueError:
                value -= 1

        self.items = self.items[1:index + 1] + tmp + self.items[index + 1:] + self.items[0:1]

    def __str__(self):
        buf = io.StringIO()
        for idx, item in enumerate(self.items):
            # if idx > 0:
            #     buf.write(", ")
            buf.write(str(item))
            buf.write("\n")

        return buf.getvalue()


def main():
    raw = "916438275"
    raw = "389125467"
    ring = Ring(*(int(r) for r in raw))

    for _ in range(2):
        ring.extract()
    print(ring)


if __name__ == "__main__":
    main()
