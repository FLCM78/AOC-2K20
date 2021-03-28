import io

class ChainedListNode:
    """ Chained List Element """

    def __init__(self, chain, value, left=None, right=None):
        self.chain = chain
        self.value = value
        self.left = left
        self.right = right

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        buf = io.StringIO()

        buf.write("[")
        if self.left is not None:
            buf.write(f"({self.left.value}) <- ")
        else:
            buf.write("(None) <- ")

        buf.write(str(self.value))

        if self.right is not None:
            buf.write(f" -> ({self.right.value})")
        else:
            buf.write(" -> (None)")

        buf.write("]")

        return buf.getvalue()

    def is_first(self):
        return self.left is None

    def is_last(self):
        return self.right is None

    def get_last(self):
        if self.right is None:
            return self

        return self.right.get_last()

    def insert_after(self, value):
        right = self.right
        node = ChainedListNode(self.chain, value, left=self, right=right)
        self.right = node

        if right is None:
            # assert self.chain.last == self
            self.chain.last = node
        else:
            # assert right.left == self
            right.left = node

        return node

    def pop(self):
        left = self.left
        right = self.right
        self.left = None
        self.right = None

        if left is not None:
            assert left.right == self
            left.right = right
        else:
            assert self.chain.first == self
            self.chain.first = right

        if right is not None:
            assert right.left == self
            right.left = left
        else:
            assert self.chain.last == self
            self.chain.last = left

        self.chain.length -= 1

        return self.value

class ChainedList:
    """ Chained List Object """

    def __init__(self):
        self.first = None
        self.last = None
        self.length = 0

    def __bool__(self):
        return self.first is not None

    def push_back(self, value):
        if self.last is None:
            assert self.first is None
            self.first = self.last = ChainedListNode(self, value)
            self.length = 1
        else:
            assert self.last.right is None
            self.last.right = ChainedListNode(self, value, left=self.last)
            self.last = self.last.right
            self.length += 1

    def pop_front(self):
        if self.first is None:
            raise ValueError("can't pop front from empty list")

        return self.first.pop()

    def pop_back(self):
        if self.last is None:
            raise ValueError("can't pop front from empty list")

        return self.last.pop()

    def __iter__(self):
        node = self.first

        while node is not None:
            yield node
            node = node.right

    def __str__(self):
        buf = io.StringIO()

        buf.write("{")
        for node in self:
            if not node.is_first():
                buf.write(", ")
            buf.write(str(node.value))
        buf.write("}")

        return buf.getvalue()

    def __len__(self):
        return self.length

    def copy(self, length=None):
        copy = ChainedList()

        for idx, node in enumerate(self):
            if length is not None and idx == length:
                break
            copy.push_back(node.value)

        return copy

    def find_first(self, value):
        for node in self:
            if node == value:
                return node

        return None

    def clear(self):
        while self.first is not None:
            self.first.pop()

        assert self.first is None
        assert self.last is None
