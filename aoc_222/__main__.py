import re
import sys
import tracing

from chained_list import ChainedList


class GameStack:
    GId = 0
    Stack = ChainedList()

    @classmethod
    def get_game_id(cls):
        cls.GId += 1
        cls.Stack.push_back(cls.GId)
        return cls.GId

    @classmethod
    def pop(cls, winner):
        # print(cls.Stack, winner, "wins BITE")
        cls.Stack.pop_back()

def game(player_1, player_2):
    game_id = GameStack.get_game_id()
    rnd = 0

    tracing.info("=== game {} ===", game_id)
    history_1 = {}
    history_2 = {}

    while True:
        rnd += 1

        if not player_1 or not player_2:
            break

        tracing.info("-- round {} (game {})", rnd, game_id)
        deck_1 = str(player_1)
        deck_2 = str(player_2)
        # tracing.info("player 1's deck", deck_1)
        # tracing.info("player 2's deck", deck_2)
        if game_id < 2:
            print(game_id, rnd, "\033[32mplayer 1\033[0m", deck_1, "\033[31mplayer 2\033[0m", deck_2)

        # if (deck_1, deck_2) in history:
        if deck_1 in history_1 or deck_2 in history_2:
            # tracing.info("already played on round {}", history[(deck_1, deck_2)])
            # tracing.info("player 1 wins round {}", rnd)
            player_2.clear()
            # tracing.info("=== game {} === winner is player_{}", game_id, 1 if player_1 else 2)
            GameStack.pop("player 1")
            return

        history_1[deck_1] = rnd
        history_2[deck_2] = rnd

        value_1 = player_1.pop_front()
        value_2 = player_2.pop_front()

        # tracing.info("player 1 plays: {}", value_1)
        # tracing.info("player 2 plays: {}", value_2)

        if value_1 <= len(player_1) and value_2 <= len(player_2):
            # tracing.info("playing sub-game to determine the winner ...", game_id)
            sub_player_1 = player_1.copy(value_1)
            sub_player_2 = player_2.copy(value_2)
            game(sub_player_1, sub_player_2)
            # tracing.info("back to game {} ...", game_id)
            # tracing.info("player {} wins round {}", 1 if sub_player_1 else 2, rnd)

            if sub_player_1:
                player_1.push_back(value_1)
                player_1.push_back(value_2)
            else:
                player_2.push_back(value_2)
                player_2.push_back(value_1)
        else:
            # tracing.info("player {} wins round {}", 1 if value_1 > value_2 else 2, rnd)
            if value_1 > value_2:
                player_1.push_back(value_1)
                player_1.push_back(value_2)
            elif value_1 < value_2:
                player_2.push_back(value_2)
                player_2.push_back(value_1)
            else:
                assert False

    GameStack.pop("player 1" if player_1 else "player 2")
    tracing.info("=== game {} === winner is player_{}", game_id, 1 if player_1 else 2)
    # print(game_id, "player 1" if player_1 else "player 2", "wins")



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

    game(players[1], players[2])

    winner = players[1] or players[2]
    tracing.info("winner: {}", winner)

    node = winner.last
    count = 0
    total = 0

    while node:
        count += 1
        total += node.value * count
        node = node.left

    print("result", total)


if __name__ == "__main__":
    main()
