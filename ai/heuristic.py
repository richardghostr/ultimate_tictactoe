"""heuristic.py — Fonction d'évaluation heuristique paramétrable.

Ce module expose `evaluate(board, player)` mais aussi des helpers
pour récupérer / modifier et sauvegarder les poids de l'heuristique.
Cela permet d'entraîner (self-play) et de persister les poids.
"""

from game.board import Board, EMPTY, PLAYER_X, PLAYER_O, DRAW
import json
import os
from copy import deepcopy

# Default weights (previous constants are now parameters)
_DEFAULT_WEIGHTS = {
    'SCORE_GLOBAL_WIN': 10000,
    'SCORE_LOCAL_WIN': 100,
    'SCORE_LOCAL_DRAW': -10,
    'POS_VALUE': [
        [20, 10, 20],
        [10, 30, 10],
        [20, 10, 20],
    ],
    'POS_VALUE_LOCAL': [
        [2, 1, 2],
        [1, 3, 1],
        [2, 1, 2],
    ],
    'SCORE_POTENTIAL_LINE': 10,
    'SCORE_ACTIVE_GRID': 5,
}

# Module-level weights used by evaluate()
_WEIGHTS = deepcopy(_DEFAULT_WEIGHTS)

# Backwards-compatible module export for SCORE_GLOBAL_WIN
SCORE_GLOBAL_WIN = _WEIGHTS['SCORE_GLOBAL_WIN']


def get_weights():
    """Retourne une copie des poids courants."""
    return deepcopy(_WEIGHTS)


def set_weights(weights: dict):
    """Remplace les poids courants par `weights` (seules les clés existantes sont prises)."""
    for k in _DEFAULT_WEIGHTS:
        if k in weights:
            _WEIGHTS[k] = deepcopy(weights[k])
    # update compatible module-level constants
    global SCORE_GLOBAL_WIN
    SCORE_GLOBAL_WIN = _WEIGHTS['SCORE_GLOBAL_WIN']


def load_weights(path: str):
    """Charge les poids depuis un fichier JSON et les applique."""
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    set_weights(data)


def save_weights(path: str):
    """Sauvegarde les poids courants dans un fichier JSON."""
    dirname = os.path.dirname(path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(_WEIGHTS, f, indent=2, ensure_ascii=False)


def _get(k):
    return _WEIGHTS[k]


def evaluate(board, player=PLAYER_X):
    """Évalue le plateau depuis le point de vue de `player`."""
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X

    SCORE_GLOBAL_WIN = _get('SCORE_GLOBAL_WIN')
    SCORE_LOCAL_WIN = _get('SCORE_LOCAL_WIN')
    SCORE_LOCAL_DRAW = _get('SCORE_LOCAL_DRAW')
    POS_VALUE = _get('POS_VALUE')
    POS_VALUE_LOCAL = _get('POS_VALUE_LOCAL')
    SCORE_POTENTIAL_LINE = _get('SCORE_POTENTIAL_LINE')
    SCORE_ACTIVE_GRID = _get('SCORE_ACTIVE_GRID')

    # --- Cas terminal ---
    if board.global_winner == player:
        return SCORE_GLOBAL_WIN
    if board.global_winner == opponent:
        return -SCORE_GLOBAL_WIN
    if board.global_winner == DRAW:
        return 0

    score = 0

    # Grille globale des vainqueurs locaux
    meta = [[board.local_winner[gr][gc] for gc in range(3)] for gr in range(3)]

    # 1. Score des sous-grilles gagnées + valeur positionnelle globale
    for gr in range(3):
        for gc in range(3):
            lw = board.local_winner[gr][gc]
            pos = POS_VALUE[gr][gc]

            if lw == player:
                score += SCORE_LOCAL_WIN + pos
            elif lw == opponent:
                score -= SCORE_LOCAL_WIN + pos
            elif lw == DRAW:
                score += SCORE_LOCAL_DRAW

    # 2. Alignements potentiels dans la grille globale (méta-morpion)
    score += _potential_lines_score(meta, player, opponent)

    # 3. Score des sous-grilles non terminées
    for gr in range(3):
        for gc in range(3):
            if board.local_winner[gr][gc] == EMPTY:
                score += _evaluate_subgrid(board.cells[gr][gc], player, opponent)

    # 4. Bonus/malus pour la grille active envoyée à l'adversaire
    if board.active_grid is not None:
        ag = board.active_grid
        lw = board.local_winner[ag[0]][ag[1]]
        if lw == EMPTY:
            sub_score = _evaluate_subgrid(board.cells[ag[0]][ag[1]], opponent, player)
            score -= int(sub_score * 0.1)

    return score


# ------------------------------------------------------------------
# Évaluation d'une sous-grille locale
# ------------------------------------------------------------------


def _evaluate_subgrid(grid, player, opponent):
    score = 0
    SCORE_POTENTIAL_LINE = _get('SCORE_POTENTIAL_LINE')
    POS_VALUE_LOCAL = _get('POS_VALUE_LOCAL')

    # Alignements potentiels locaux
    score += _potential_lines_score(grid, player, opponent) * (SCORE_POTENTIAL_LINE // 10)

    # Valeur positionnelle des cases occupées
    for r in range(3):
        for c in range(3):
            val = grid[r][c]
            if val == player:
                score += POS_VALUE_LOCAL[r][c]
            elif val == opponent:
                score -= POS_VALUE_LOCAL[r][c]

    return score


# ------------------------------------------------------------------
# Alignements potentiels (lignes avec 2 symboles et 1 case vide)
# ------------------------------------------------------------------

WINNING_LINES = [
    [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
]


def _potential_lines_score(grid, player, opponent):
    score = 0
    SCORE_POTENTIAL_LINE = _get('SCORE_POTENTIAL_LINE')
    for line in WINNING_LINES:
        vals = [grid[r][c] for r, c in line]
        p_count = vals.count(player)
        o_count = vals.count(opponent)
        e_count = vals.count(EMPTY)

        # Ligne non bloquée
        if o_count == 0:
            if p_count == 2:
                score += SCORE_POTENTIAL_LINE
            elif p_count == 1:
                score += 1
        if p_count == 0:
            if o_count == 2:
                score -= SCORE_POTENTIAL_LINE
            elif o_count == 1:
                score -= 1

    return score


def terminal_score(board, player=PLAYER_X):
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
    SCORE_GLOBAL_WIN = _get('SCORE_GLOBAL_WIN')
    if board.global_winner == player:
        return SCORE_GLOBAL_WIN
    if board.global_winner == opponent:
        return -SCORE_GLOBAL_WIN
    return 0