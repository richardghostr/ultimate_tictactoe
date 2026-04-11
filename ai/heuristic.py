"""
heuristic.py — Fonction d'évaluation heuristique pour l'Ultimate Tic Tac Toe.

Utilisée par Minimax quand la profondeur limite est atteinte.
Retourne un score du point de vue de PLAYER_X :
    score > 0  : avantage pour X
    score < 0  : avantage pour O
    score = 0  : position équilibrée

Composantes du score
--------------------
1. Victoire/défaite globale       : +/-10000 (terminal)
2. Sous-grilles gagnées           : +/-100 par sous-grille
3. Valeur positionnelle globale   : centre=30, coin=20, bord=10
4. Alignements potentiels locaux  : +/-10 par alignement à 2 cases
5. Valeur positionnelle locale    : centre=3, coin=2, bord=1
6. Contrainte de grille active    : +/-5 (envoyer l'adversaire dans une mauvaise zone)
"""

from game.board import Board, EMPTY, PLAYER_X, PLAYER_O, DRAW

# ------------------------------------------------------------------
# Poids du score
# ------------------------------------------------------------------
SCORE_GLOBAL_WIN   = 10000
SCORE_LOCAL_WIN    = 100
SCORE_LOCAL_DRAW   = -10     # un nul local est légèrement négatif (perte d'opportunité)

# Valeur positionnelle des cases dans la grille 3x3 (globale et locale)
# Centre > Coin > Bord
POS_VALUE = [
    [20, 10, 20],
    [10, 30, 10],
    [20, 10, 20],
]

POS_VALUE_LOCAL = [
    [2, 1, 2],
    [1, 3, 1],
    [2, 1, 2],
]

SCORE_POTENTIAL_LINE = 10   # alignement de 2 dans une ligne ouverte
SCORE_ACTIVE_GRID    = 5    # bonus pour envoyer l'adversaire dans une zone perdue


def evaluate(board, player=PLAYER_X):
    """
    Évalue le plateau du point de vue de `player`.

    Paramètres
    ----------
    board  : Board
    player : int — PLAYER_X ou PLAYER_O (joueur qui maximise)

    Retourne
    --------
    float — score (positif = bon pour player)
    """
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X

    # --- Cas terminal ---
    if board.global_winner == player:
        return SCORE_GLOBAL_WIN
    if board.global_winner == opponent:
        return -SCORE_GLOBAL_WIN
    if board.global_winner == DRAW:
        return 0

    score = 0

    # --- Grille globale des vainqueurs locaux ---
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
        # Si on envoie l'adversaire dans une sous-grille qu'il a avantage = mauvais
        if lw == EMPTY:
            sub_score = _evaluate_subgrid(board.cells[ag[0]][ag[1]], opponent, player)
            # sub_score > 0 = avantageux pour opponent (adversaire du joueur qui évalue)
            # On pénalise légèrement si on l'envoie dans une bonne zone pour lui
            score -= int(sub_score * 0.1)

    return score


# ------------------------------------------------------------------
# Évaluation d'une sous-grille locale
# ------------------------------------------------------------------

def _evaluate_subgrid(grid, player, opponent):
    """
    Évalue une sous-grille 3x3 non terminée.
    Retourne un score partiel (positif = bon pour player).
    """
    score = 0

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
    """
    Pour chaque ligne de la grille 3x3, évalue les alignements potentiels :
    - 2 symboles du joueur + 1 vide  : +SCORE_POTENTIAL_LINE
    - 1 symbole du joueur + 2 vides  : +1
    - 2 symboles adversaire + 1 vide : -SCORE_POTENTIAL_LINE
    - 1 symbole adversaire + 2 vides : -1
    - Lignes bloquées (2 joueurs)    : 0
    """
    score = 0
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


# ------------------------------------------------------------------
# Utilitaire : score terminal uniquement (pour tests)
# ------------------------------------------------------------------

def terminal_score(board, player=PLAYER_X):
    """
    Retourne uniquement le score terminal (+/-SCORE_GLOBAL_WIN ou 0).
    Utile pour vérifier rapidement si un état est gagnant/perdant.
    """
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
    if board.global_winner == player:
        return SCORE_GLOBAL_WIN
    if board.global_winner == opponent:
        return -SCORE_GLOBAL_WIN
    return 0