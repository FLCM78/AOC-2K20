import io
import sys
import ply.lex as lex
import tracing


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

    def is_operator(self):
        return not isinstance(self.value, int)

    def is_integer(self):
        return not isinstance(self.value, int)

    def get_last(self):
        if self.right is None:
            return self

        return self.right.get_last()

    def pop(self):
        left = self.left
        right = self.right
        self.left = None
        self.right = None

        if left is not None:
            assert left.right == self
            left.right = right
        else:
            assert self.chain.root == self
            self.chain.root = right

        if right is not None:
            assert right.left == self
            right.left = left

class ChainedList:
    """ Chained List Object """

    OPERATORS = {
        "+": lambda x, y: x + y,
        "*": lambda x, y: x * y,
    }

    def __init__(self):
        self.root = None

    def append(self, value):
        if self.root is None:
            self.root = ChainedListNode(self, value)
        else:
            last = self.root.get_last()
            last.right = ChainedListNode(self, value)
            last.right.left = last

    def __iter__(self):
        node = self.root

        while node is not None:
            yield node
            node = node.right


    def __str__(self):
        buf = io.StringIO()

        buf.write("{")
        for node in self:
            if not node.is_first():
                buf.write(" <=> ")
            buf.write(str(node.value))
        buf.write("}")

        return buf.getvalue()

    def __len__(self):
        cnt = 0
        for _ in self:
            cnt += 1

        return cnt

    def find_first(self, value):
        for node in self:
            if node == value:
                return node

        return None

    def eval(self):
        for operator in ["+", "*"]:
            node = self.find_first(operator)
            while node is not None:
                tracing.debug("Eval: {} - {} {} {}", self, node.left, node, node.right)
                if node.is_first():
                    err = f"{operator} operator can't be first"
                    raise RuntimeError(err)
                if node.left.is_operator():
                    err = f"left operand of {operator} must be number"
                    raise RuntimeError(err)
                left = node.left

                if node.is_last():
                    err = f"{operator} operator can't be last"
                    raise RuntimeError(err)
                if node.right.is_operator():
                    err = f"right operand of {operator} must be number"
                    raise RuntimeError(err)
                right = node.right

                node.value = self.OPERATORS[operator](left.value, right.value)
                right.pop()
                left.pop()
                tracing.debug("Eval: {} - {} {} {}", self, node.left, node, node.right)
                node = self.find_first(operator)

        assert len(self) == 1

        return self.root.value

class ExprParser:
    """ Parser """

    tokens = (
        "RPAREN",
        "LPAREN",
        "ADD",
        "MUL",
        "NUMBER",
    )

    states = []

    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_ADD = r"\+"
    t_MUL = r"\*"
    t_ignore = " \t"


    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.tkn = None

    @lex.TOKEN(r"\d+")
    def t_NUMBER(self, tkn):
        tkn.value = int(tkn.value)

        return tkn

    def t_error(self, tkn):
        msg = "syntax error at pos %s: '%s'"
        ctx_str = self.get_expr_ctx(tkn)
        tracing.error(msg, tkn.lexpos, ctx_str)

    def get_nxt_tkn(self):
        self.tkn = self.lexer.token()
        return self.tkn

    def throw(self, msg, tkn=None):
        tkn = tkn if tkn is not None else self.tkn
        exn_str = "{} at {}: '{}'".format(msg, tkn.lexpos, self.get_expr_ctx(tkn=tkn))
        tracing.error(exn_str)

        raise RuntimeError(exn_str)

    def get_expr_ctx(self, tkn=None):
        tkn = tkn if tkn is not None else self.tkn

        if tkn.lexpos > 13:
            beg = tkn.lexpos - 12
            pfx = "…{}".format(self.lexer.lexdata[beg:tkn.lexpos])
        else:
            pfx = "{}".format(self.lexer.lexdata[:tkn.lexpos])


        sfx = self.lexer.lexdata[tkn.lexpos + len(tkn.value):]
        if len(sfx) > 13:
            sfx = "{}…".format(sfx[:12])

        return "{}\033[31m{}\033[0m{}".format(pfx, tkn.value, sfx)

    def get_expr(self, inner=False):
        elements = ChainedList()

        while True:
            self.get_nxt_tkn()

            if self.tkn is None:
                if inner is False:
                    break
                self.throw("nothing more to read, but ')' was expected")

            if self.tkn.type == "RPAREN":
                if inner is True:
                    break
                self.throw("unexpected ')'")

            if self.tkn.type == "LPAREN":
                tracing.debug("start group at {}: '{}'", self.tkn.lexpos, self.get_expr_ctx())
                expr = self.get_expr(inner=True)

                if expr is None:
                    self.throw("empty expression")

                if self.tkn.type != "RPAREN":
                    self.throw("unmatched parenthesis")

                tracing.debug("stop group at {}: '{}'", self.tkn.lexpos, self.get_expr_ctx())
                elements.append(expr)
                continue

            if self.tkn.type in ["NUMBER", "ADD", "MUL"]:
                elements.append(self.tkn.value)

        tracing.info("elements: {}", elements)
        return elements.eval()

    def parse(self, expr):
        self.lexer.input(expr)
        return self.get_expr()

def main():
    total = 0
    for idx, _raw in enumerate(sys.stdin):
        raw = _raw.strip()
        parser = ExprParser()
        res = parser.parse(raw)
        tracing.info("res: {}", res)
        total += res

    tracing.info("total = {}", total)

if __name__ == "__main__":
    main()
