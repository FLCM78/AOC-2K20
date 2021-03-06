import sys
import tracing

class TreeNode:
    """ Tree Node class """

    def __init__(self, value):
        self.value = value
        self.children = []
        self.path_cnt = None

    def __str__(self):
        return "{} children: [{}]".format(
            self.value,
            ", ".join(str(c.value) for c in self.children)
        )

    def is_in_range(self, other):
        return abs(self.value - other.value) <= 3

    def count_path(self):
        if not self.children:
            return 1

        if self.path_cnt is None:
            self.path_cnt = sum(c.count_path() for c in self.children)

        return self.path_cnt

    def show_path(self):
        if not self.children:
            yield [self.value]
            return

        for child in self.children:
            for path in child.show_path():
                yield path + [self.value]

def main():
    zero = TreeNode(0)
    stack = [TreeNode(int(r)) for r in sys.stdin]
    stack.sort(key=lambda x: x.value)

    for idx, tnd in enumerate(stack):
        if tnd.is_in_range(zero):
            tnd.children.append(zero)

        for k in range(idx):
            if tnd.is_in_range(stack[k]):
                tnd.children.append(stack[k])

        tnd.children.sort(key=lambda x: x.value, reverse=True)
        tracing.info("TreeNode {}", tnd)

    # for path in stack[-1].show_path():
    #     pstr = ""
    #     for tnd in stack:
    #         if tnd.value in path:
    #             pstr += " {:2d} ".format(tnd.value)
    #         else:
    #             pstr += " __ "
    #     print(pstr)

    for idx, tnd in enumerate(stack):
        tracing.info("{} - COUNT PATH: {}", tnd, tnd.count_path())

if __name__ == "__main__":
    main()
