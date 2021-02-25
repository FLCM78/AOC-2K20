import sys
import tracing

class PasswordCheck:

    def __init__(self, char="", min_len=0, max_len=-1):
        self.max_len = max_len
        self.min_len = min_len
        self.char = char

    def __str__(self):
        return f"char '{self.char}' range[{self.min_len}, {self.max_len}]"


    def check(self, value):
        first_match = len(value) > self.min_len and value[self.min_len] == self.char
        second_match = len(value) > self.max_len and value[self.max_len] == self.char

        return (first_match and not second_match) or (not first_match and second_match)

    @classmethod
    def check_raw(cls, raw):
        raw, value = raw.split(":")
        raw, char = raw.split(" ")
        min_len, max_len = map(int, raw.split("-"))

        checker = cls(char, min_len - 1, max_len - 1)
        check = checker.check(value.strip())

        tracing.info("Contstraint: {checker}", checker=checker)
        if check:
            tracing.info("valid password '{}'", value.strip())
        else:
            tracing.warn("invalid password '{}'", value.strip())

        return check

def main():

    count = 0

    for raw in sys.stdin:
        count += 1 if PasswordCheck.check_raw(raw.strip()) else 0

    tracing.info("Number of matching passwords {count}", count=count)

if __name__ == "__main__":
    main()
