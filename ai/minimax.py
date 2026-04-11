"""
minimax.py — Algorithme Minimax avec élagage Alpha-Beta.

Implémentation directement inspirée du cours CMO4 (Christophe Rodrigues) :

    MINIMAX(s) =
        UTILITY(s)                              si TERMINAL-TEST(s)
        max_{a ∈ Actions(s)} MINIMAX(Result(s,a))   si PLAYER(s) = MAX
        min_{a ∈ Actions(s)} MINIMAX(Result(s,a))   si PLAYER(s) = MIN

L'élagage Alpha-Beta coupe les branches inutiles :
    α = meilleur score garanti pour MAX (borne basse)
    β = meilleur score garanti pour MIN (borne haute)
    Coupure si α >= β

Contraintes du projet :
- Pas de dictionnaire de coups pré-calculés
- Décision calculée à la volée
- Profondeur limitée + heuristique pour rester dans le temps imparti
"""

import math
from ai.heuristic import evaluate, terminal_score, SCORE_GLOBAL_WIN
from game.rules import get_legal_moves, apply_move
from game.board import PLAYER_X, PLAYER_O, EMPTY


# ------------------------------------------------------------------
# Ordonnancement des coups (move ordering)
# Trier les coups améliore considérablement l'élagage Alpha-Beta.
# On joue d'abord les coups dans les cases stratégiques (centre, coin).
# ------------------------------------------------------------------

_MOVE_PRIORITY = [
    (1, 1),   # centre local
    (0, 0), (0, 2), (2, 0), (2, 2),  # coins locaux
    (0, 1), (1, 0), (1, 2), (2, 1),  # bords locaux
]
_PRIORITY_MAP = {pos: i for i, pos in enumerate(_MOVE_PRIORITY)}


def _move_order_key(move):
    """Clé de tri pour favoriser les cases stratégiques."""
    _, _, lr, lc = move
    return _PRIORITY_MAP.get((lr, lc), 9)


# ------------------------------------------------------------------
# Minimax avec Alpha-Beta
# ------------------------------------------------------------------

def minimax(board, depth, alpha, beta, maximizing_player, root_player=PLAYER_X):
    """
    Algorithme Minimax avec élagage Alpha-Beta.

    Paramètres
    ----------
    board              : Board — état courant
    depth              : int   — profondeur restante
    alpha              : float — borne basse MAX (-inf au départ)
    beta               : float — borne haute MIN (+inf au départ)
    maximizing_player  : bool  — True si c'est le tour de MAX
    root_player        : int   — joueur qui appelle Minimax (PLAYER_X ou PLAYER_O)

    Retourne
    --------
    float — valeur heuristique du nœud
    """
    # --- Cas de base : nœud terminal ou profondeur atteinte ---
    if board.is_terminal():
        return terminal_score(board, player=root_player)

    if depth == 0:
        return evaluate(board, player=root_player)

    moves = get_legal_moves(board)
    if not moves:
        return evaluate(board, player=root_player)

    # Ordonner les coups pour maximiser les coupures
    moves = sorted(moves, key=_move_order_key)

    if maximizing_player:
        value = -math.inf
        for move in moves:
            child = apply_move(board, move)
            value = max(value, minimax(child, depth - 1, alpha, beta, False, root_player))
            alpha = max(alpha, value)
            if alpha >= beta:
                break   # Coupure Beta (le MIN ne choisira pas cette branche)
        return value

    else:
        value = math.inf
        for move in moves:
            child = apply_move(board, move)
            value = min(value, minimax(child, depth - 1, alpha, beta, True, root_player))
            beta = min(beta, value)
            if alpha >= beta:
                break   # Coupure Alpha (le MAX ne choisira pas cette branche)
        return value


# ------------------------------------------------------------------
# Point d'entrée principal : trouver le meilleur coup
# ------------------------------------------------------------------

def get_best_move(board, depth=3, root_player=None):
    """
    Retourne le meilleur coup pour le joueur courant via Minimax Alpha-Beta.

    Paramètres
    ----------
    board       : Board — état courant
    depth       : int   — profondeur de recherche (3 par défaut)
    root_player : int   — PLAYER_X ou PLAYER_O (None = joueur courant)

    Retourne
    --------
    tuple(gr, gc, lr, lc) — meilleur coup trouvé
    None                   — si aucun coup légal
    """
    if root_player is None:
        root_player = board.current_player

    moves = get_legal_moves(board)
    if not moves:
        return None

    # Un seul coup possible : inutile de calculer
    if len(moves) == 1:
        return moves[0]

    moves = sorted(moves, key=_move_order_key)

    best_move = moves[0]
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf

    # L'IA est MAX quand c'est son tour
    for move in moves:
        child = apply_move(board, move)
        # Après notre coup, c'est au MIN de jouer
        value = minimax(child, depth - 1, alpha, beta, False, root_player)

        if value > best_value:
            best_value = value
            best_move = move

        alpha = max(alpha, best_value)

        # Coup gagnant immédiat : inutile de continuer
        if best_value >= SCORE_GLOBAL_WIN:
            break

    return best_move


# ------------------------------------------------------------------
# Minimax itératif (deepening) — pour respecter une limite de temps
# ------------------------------------------------------------------

def get_best_move_timed(board, time_limit=5.0, max_depth=8, root_player=None):
    """
    Approfondissement itératif : augmente la profondeur tant que
    le temps restant le permet.

    Garantit toujours un coup valide (même si la limite est très basse).

    Paramètres
    ----------
    board      : Board
    time_limit : float — secondes maximum (défaut 5.0)
    max_depth  : int   — profondeur maximale absolue
    root_player: int   — PLAYER_X ou PLAYER_O

    Retourne
    --------
    tuple(gr, gc, lr, lc)
    """
    import time

    if root_player is None:
        root_player = board.current_player

    moves = get_legal_moves(board)
    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]

    best_move = sorted(moves, key=_move_order_key)[0]
    start = time.time()

    for depth in range(1, max_depth + 1):
        elapsed = time.time() - start
        if elapsed >= time_limit:
            break

        try:
            move = get_best_move(board, depth=depth, root_player=root_player)
            if move is not None:
                best_move = move
        except Exception:
            break

        # Si on a trouvé un coup gagnant, inutile d'aller plus loin
        child = apply_move(board, best_move)
        if child.is_terminal():
            break

    return best_move