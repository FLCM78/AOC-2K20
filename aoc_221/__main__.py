import re
import sys
import tracing

from chained_list import ChainedList

def main():
    players = {}

    for _raw in sys.stdin:
        raw = _raw.strip()
        match = re.match(r"Player ([0-9]):", raw)
        player_id = int(match.group(1))
        players[player_id] = ChainedList()

        for card in sys.stdin:
            if card == "\n":
                break
            players[player_id].push_back(int(card))

        tracing.info("{}: {}", player_id, players[player_id])

    rnd = 0
    while True:
        rnd += 1

        if not players[1] or not players[2]:
            break

        value_1 = players[1].pop_front()
        value_2 = players[2].pop_front()

        tracing.info("Round {}", rnd)
        tracing.info("player 1: {}", players[1])
        tracing.info("player 2: {}", players[2])
        tracing.info("value[1]: {}, value[2]: {}", value_1, value_2)

        if value_1 > value_2:
            players[1].push_back(value_1)
            players[1].push_back(value_2)
        elif value_2 > value_1:
            players[2].push_back(value_2)
            players[2].push_back(value_1)

    winner = players[1] or players[2]
    tracing.info("winner: {}", winner)

    node = winner.last
    count = 0
    total = 0

    while node:
        count += 1
        total += node.value * count
        node = node.left

    tracing.info("result: {}", total)

if __name__ == "__main__":
    main()
