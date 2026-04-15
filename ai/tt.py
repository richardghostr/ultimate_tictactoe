"""Transposition table with Zobrist hashing and persistence.

Provides a simple TranspositionTable class and Zobrist hashing helpers.
"""
import os
import pickle
import random
from typing import Optional, Tuple

# Entry: (value: float, depth: int, flag: int, best_move)
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def get(self, key: int) -> Optional[Tuple[float, int, int, object]]:
        return self.table.get(key)

    def store(self, key: int, value: float, depth: int, flag: int, best_move):
        # store or replace when deeper
        existing = self.table.get(key)
        if existing is None or depth >= existing[1]:
            self.table[key] = (value, depth, flag, best_move)

    def save(self, path: str):
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.table, f, protocol=4)

    def load(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            self.table = pickle.load(f)


# Zobrist hashing for a 9x9 board: 81 squares x 2 players + side-to-move
_rng = random.Random(0)  # deterministic seed
_ZOBRIST_PIECE = [[_rng.getrandbits(64) for _ in range(2)] for _ in range(81)]
_ZOBRIST_SIDE = _rng.getrandbits(64)


def compute_zobrist_from_cells(cells) -> int:
    """Compute a 64-bit Zobrist key from the nested cells structure.

    `cells` expected as board.cells[gr][gc][lr][lc]
    """
    h = 0
    for gr in range(3):
        for gc in range(3):
            for lr in range(3):
                for lc in range(3):
                    val = cells[gr][gc][lr][lc]
                    if val == 0:
                        continue
                    # map to 0..80 index
                    global_row = gr * 3 + lr
                    global_col = gc * 3 + lc
                    idx = global_row * 9 + global_col
                    # PLAYER_X -> index 0, PLAYER_O -> index 1
                    player_index = 0 if val == 1 else 1
                    h ^= _ZOBRIST_PIECE[idx][player_index]
    return h


# Module-level default TT
default_tt = TranspositionTable()


def save_default(path: str):
    default_tt.save(path)


def load_default(path: str):
    default_tt.load(path)

