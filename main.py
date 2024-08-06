import numpy as np
from game import Board
from game import IllegalAction, GameOver
from agent import nTupleNewrok
import pickle

from collections import namedtuple

"""
Vocabulary
--------------

Transition: A Transition shows how a board transfromed from a state to the next state. It contains the board state (s), the action performed (a), 
the reward received by performing the action (r), the board's "after state" after applying the action (s_after), and the board's "next state" (s_next) after adding a random tile to the "after state".

Gameplay: A series of transitions on the board (transition_history). Also reports the total reward of playing the game (game_reward) and the maximum tile reached (max_tile).
"""
Transition = namedtuple("Transition", "s, a, r, s_after, s_next")
Gameplay = namedtuple("Gameplay", "transition_history game_reward max_tile")


def play(agent, board, spawn_random_tile=False):
    "Return a gameplay of playing the given (board) until terminal states."
    b = Board(board)
    r_game = 0
    a_cnt = 0
    transition_history = []
    while True:
        a_best = agent.best_action(b.board)
        s = b.copyboard()
        try:
            r = b.act(a_best)
            r_game += r
            s_after = b.copyboard()
            b.spawn_tile(random_tile=spawn_random_tile)
            s_next = b.copyboard()
        except (IllegalAction, GameOver) as e:
            # game ends when agent makes illegal moves or board is full
            r = None
            s_after = None
            s_next = None
            break
        finally:
            a_cnt += 1
            transition_history.append(
                Transition(s=s, a=a_best, r=r, s_after=s_after, s_next=s_next)
            )
    gp = Gameplay(
        transition_history=transition_history,
        game_reward=r_game,
        max_tile=2 ** max(b.board),
    )
    learn_from_gameplay(agent, gp)
    return gp


def learn_from_gameplay(agent, gp, alpha=0.1):
    "Learn transitions in reverse order except the terminal transition"
    for tr in gp.transition_history[:-1][::-1]:
        agent.learn(tr.s, tr.a, tr.r, tr.s_after, tr.s_next, alpha=alpha)


def load_agent(path):
    return pickle.load(path.open("rb"))


# map board state to LUT
TUPLES = [
    # horizontal 4-tuples
    
    # vertical 4-tuples
    
    # all 4-tile squares
    
]

if __name__ == "__main__":
    import numpy as np

    agent = None
    # prompt to load saved agents
    from pathlib import Path

    path = Path("tmp")
    saves = list(path.glob("*.pkl"))
    if len(saves) > 0:
        print("Found %d saved agents:" % len(saves))
        for i, f in enumerate(saves):
            print("{:2d} - {}".format(i, str(f)))
        k = input(
            "input the id to load an agent, input nothing to create a fresh agent:"
        )
        if k.strip() != "":
            k = int(k)
            n_games, agent = load_agent(saves[k])
            print("load agent {}, {} games played".format(saves[k].stem, n_games))
    if agent is None:
        print("initialize agent")
        n_games = 0
        agent = nTupleNewrok(TUPLES)

    n_session = 5000
    n_episode = 100
    print("training")
    try:
        for i_se in range(n_session):
            for _ in range(n_episode):
                play(agent, [0] * 16)
                n_games += 1
           
    except KeyboardInterrupt:
        print("training interrupted")
        print("{} games played by the agent".format(n_games))
        if input("save the agent? (y/n)") == "y":
            fout = "tmp/{}_{}games.pkl".format(agent.__class__.__name__, n_games)
            pickle.dump((n_games, agent), open(fout, "wb"))
            print("agent saved to", fout)