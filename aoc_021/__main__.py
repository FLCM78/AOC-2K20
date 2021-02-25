import sys
import tracing

class PasswordCheck:

    def __init__(self, char="", min_len=0, max_len=-1):
        self.max_len = max_len
        self.min_len = min_len
        self.char = char


    def check(self, value):
        count = value.count(self.char)

        if count > self.max_len or count < self.min_len:
            return False

        return True

    @classmethod
    def check_raw(cls, raw):
        raw, value = raw.split(":")
        raw, char = raw.split(" ")
        min_len, max_len = map(int, raw.split("-"))

        checker = cls(char, min_len, max_len)
        check = checker.check(value)

        tracing.info(f"char '{char}' range[{min_len}, {max_len}]")
        if check:
            tracing.info("valid password '{}'", value)
        else:
            tracing.warn("invalid password '{}'", value)

        return check


def main():

    count = 0

    for raw in sys.stdin:
        count += 1 if PasswordCheck.check_raw(raw.strip()) else 0

    tracing.info("Number of matching passwords {count}", count=count)

if __name__ == "__main__":
    main()
