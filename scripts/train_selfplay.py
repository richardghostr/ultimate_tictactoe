"""Self-play trainer (hill-climbing) for heuristic weights.

Usage: called programmatically or via CLI. The trainer tries small
perturbations of the current weights and accepts them if they win more
games against the baseline over a small sample.
"""
import os
import sys
import random
import copy

# Ensure project root is on sys.path so local packages (game, ai) can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from game.game import Game
from ai.player import AIPlayer
import ai.heuristic as heuristic
from game.board import PLAYER_X, PLAYER_O, DRAW


def _play_games(ai1, ai2, games=10, show=False):
    wins = {'ai1': 0, 'ai2': 0, 'draw': 0}
    for i in range(games):
        if i % 2 == 0:
            g = Game(ai1, ai2, show_board=show)
            res = g.run()
            if res == PLAYER_X:
                wins['ai1'] += 1
            elif res == PLAYER_O:
                wins['ai2'] += 1
            else:
                wins['draw'] += 1
        else:
            g = Game(ai2, ai1, show_board=show)
            res = g.run()
            # when ai2 starts, PLAYER_X corresponds to ai2
            if res == PLAYER_X:
                wins['ai2'] += 1
            elif res == PLAYER_O:
                wins['ai1'] += 1
            else:
                wins['draw'] += 1
    return wins


def train(iterations=50, games_per_test=6, noise=0.1, seed=0):
    """Run hill-climbing training.

    - iterations: how many candidate trials
    - games_per_test: number of games to evaluate a candidate
    - noise: relative perturbation size
    """
    random.seed(seed)

    base_weights = heuristic.get_weights()
    best_weights = copy.deepcopy(base_weights)

    # Baseline evaluation with current weights
    ai_base = AIPlayer('BASE', depth=3)
    ai_cand = AIPlayer('CAND', depth=3)

    best_score = None

    for it in range(iterations):
        # Propose candidate weights (small gaussian noise)
        cand = copy.deepcopy(best_weights)
        for k, v in cand.items():
            if isinstance(v, (int, float)):
                # perturb scalar
                cand[k] = v * (1.0 + random.uniform(-noise, noise))
            elif isinstance(v, list):
                # recursively perturb numeric lists
                def perturb_list(L):
                    out = []
                    for e in L:
                        if isinstance(e, (int, float)):
                            out.append(e * (1.0 + random.uniform(-noise, noise)))
                        elif isinstance(e, list):
                            out.append(perturb_list(e))
                        else:
                            out.append(e)
                    return out
                cand[k] = perturb_list(v)

        # Test candidate by setting weights temporarily
        old = heuristic.get_weights()
        heuristic.set_weights(cand)
        ai_base = AIPlayer('BASE', depth=3)
        ai_cand = AIPlayer('CAND', depth=3)

        wins = _play_games(ai_cand, ai_base, games=games_per_test, show=False)
        score = wins['ai1'] - wins['ai2']

        # restore old weights
        heuristic.set_weights(old)

        if best_score is None or score > best_score:
            best_score = score
            best_weights = copy.deepcopy(cand)
            # persist improved weights
            heuristic.set_weights(best_weights)
            heuristic.save_weights('ai/heuristic_weights.json')

    # restore best weights
    heuristic.set_weights(best_weights)
    heuristic.save_weights('ai/heuristic_weights.json')
    return best_weights


if __name__ == '__main__':
    print('Training (hill-climb)...')
    w = train(iterations=30, games_per_test=6, noise=0.15)
    print('Done. Weights saved to ai/heuristic_weights.json')
