import io

class ChainedListNode:
    """ Chained List Element """

    def __init__(self, value, right=None):
        self.value = value
        self.right = right

    def __str__(self):
        buf = io.StringIO()

        buf.write("[")
        buf.write(str(self.value))

        if self.right is not None:
            buf.write(f" -> ({self.right.value})")
        else:
            buf.write(" -> (None)")
        buf.write("]")

        return buf.getvalue()
    def __eq__(self, other):
        assert isinstance(other, int)
        return self.value == other

    def insert_after(self, value):
        node = ChainedListNode(value, right=self.right)
        self.right = node

        return node

class ChainedList:
    """ Chained List Object """

    def __init__(self):
        self.first = None
        self.length = 0

    def __bool__(self):
        return self.first is not None

    def push_front(self, value):
        self.first = ChainedListNode(value, right=self.first)

    def pop_front(self):
        assert self.first is not None
        tmp = self.first

        self.first = self.first.right
        return tmp

    def __iter__(self):
        node = self.first
        while node is not None:
            yield node
            node = node.right

    def __str__(self):
        buf = io.StringIO()

        node = self.first
        while node is not None:
            if node != self.first:
                buf.write(", ")
            buf.write(str(node.value))
            node = node.right

        return buf.getvalue()

class Ring:
    NB_CUPS = 1000000

    def __init__(self, *args):
        self.clist = ChainedList()
        self.val_idx = {}

        for i in range(self.NB_CUPS, 9, -1):
            self.clist.push_front(i)
            self.val_idx[i] = self.clist.first

        for val in reversed(args):
            self.clist.push_front(val)
            self.val_idx[val] = self.clist.first

        self.cur = self.clist.first


    def first_one(self):
        one = self.clist.first
        self.clist.first = one.right.right.right
        return (one, one.right, one.right.right)

    def second_one(self, one):
        one.right = self.clist.first
        self.clist.first = one.right.right.right
        self.cur.right = None
        return (one, one.right, one.right.right)

    def third_one(self, one):
        one.right.right = self.clist.first
        self.clist.first = one.right.right.right
        self.cur.right = None
        return (one, one.right, one.right.right)

    def get_tmp(self):
        one = self.cur.right
        if one is None:
            return self.first_one()

        two = one.right
        if two is None:
            return self.second_one(one)

        three = two.right
        if three is None:
            return self.third_one(one)

        self.cur.right = three.right
        return (one, two, three)

        # if one is None:
        #     one = self.clist.pop_front()
        # else:
        #     self.cur.right = one.right

        # two = self.cur.right
        # if two is None:
        #     two = self.clist.pop_front()
        #     one.right = two
        # else:
        #     self.cur.right = two.right

        # three = self.cur.right
        # if three is None:
        #     three = self.clist.pop_front()
        #     two.right = three
        # else:
        #     self.cur.right = three.right

    def get_nxt_value(self, tmp):
        nxt = self.cur.value
        one, two, three = tmp

        while True:
            nxt -= 1
            if nxt <= 0:
                nxt = self.NB_CUPS

            if nxt == one.value or nxt == two.value or nxt == three.value:
                continue

            return nxt

    def resinsert(self, nxt, tmp):
        root = self.val_idx[nxt]
        tmp[2].right = root.right
        root.right = tmp[0]

    def extract(self):
        tmp = self.get_tmp()
        nxt = self.get_nxt_value(tmp)
        self.resinsert(nxt, tmp)

        if self.cur.right is not None:
            self.cur = self.cur.right
        else:
            self.cur = self.clist.first

    def __str__(self):
        buf = io.StringIO()
        buf.write("{")

        for node in self.clist:
            if not node == self.clist.first:
                buf.write(", ")
            if node == self.cur:
                buf.write(f"({node.value})")
            else:
                buf.write(str(node.value))
        buf.write("}")
        return buf.getvalue()

        # return str(self.clist)


def main():
    raw = "916438275"
    raw = "389125467"
    ring = Ring(*(int(r) for r in raw))

    print("GO")
    # print(ring)
    for i in range(10000000):
        if i and (i % 1000) == 0:
            print("GO", i)
        ring.extract()

    # print(ring)
    result = 1
    node = ring.val_idx[1]
    print(node)

    for i in range(2):
        node = node.right
        if node is None:
            node = ring.clist.first
        print(node)
        result *= node.value

    print(result)

if __name__ == "__main__":
    main()
