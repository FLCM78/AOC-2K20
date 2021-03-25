from collections import defaultdict
import re
import sys
import tracing

class Allergenes(dict):
    def reduce(self, allergene):
        assert len(self[allergene]) == 1

        ingredient, = self[allergene]

        tracing.error("{} => {}", allergene, ingredient)

        for alg, igds in self.items():
            if alg == allergene:
                continue
            if ingredient not in igds:
                continue

            igds.remove(ingredient)
            if len(igds) == 1:
                self.reduce(alg)

    def aggregate(self, alg, igds):
        if alg not in self:
            self[alg] = set(igds)
        else:
            self[alg] &= set(igds)

        if len(self[alg]) == 1:
            self.reduce(alg)

def main():
    allergenes = Allergenes()

    for _raw in sys.stdin:
        raw = _raw.strip()
        match = re.match(r"([a-z ]*) \(contains ([^\)]+)", raw)
        igds = [i.strip() for i in match.group(1).split()]
        algs = [i.strip() for i in match.group(2).split(", ")]

        for alg in algs:
            allergenes.aggregate(alg, igds)

    tracing.info("Allergenes: {}", len(allergenes))
    alg_keys = list(allergenes.keys())
    alg_keys.sort()

    ingredients = []
    for alg in alg_keys:
        (igd,) = allergenes[alg]
        tracing.info("{}: {}", alg, igd)
        ingredients.append(igd)

    tracing.info(",".join(ingredients))

if __name__ == "__main__":
    main()
