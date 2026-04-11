"""
rules.py — Moteur de règles de l'Ultimate Tic Tac Toe.

Inspiré du formalisme du cours (CMO4) :
    Actions(s)       -> get_legal_moves(board)
    Result(s, a)     -> apply_move(board, move)
    Terminal-test(s) -> board.is_terminal()
    Utility(s, j)    -> dans heuristic.py

Un coup est un tuple (gr, gc, lr, lc) :
    gr, gc : sous-grille cible (0..2)
    lr, lc : case dans cette sous-grille (0..2)

Règle de direction :
    Après avoir joué en (lr, lc) dans n'importe quelle sous-grille,
    le prochain joueur doit jouer dans la sous-grille (lr, lc).
    Si cette sous-grille est terminée, le joueur est libre de choisir
    n'importe quelle sous-grille non terminée (active_grid = None).
"""

from .board import Board, EMPTY, PLAYER_X, PLAYER_O, DRAW

# ------------------------------------------------------------------
# Lignes gagnantes dans une grille 3x3
# ------------------------------------------------------------------
WINNING_LINES = [
    # Lignes
    [(0,0),(0,1),(0,2)],
    [(1,0),(1,1),(1,2)],
    [(2,0),(2,1),(2,2)],
    # Colonnes
    [(0,0),(1,0),(2,0)],
    [(0,1),(1,1),(2,1)],
    [(0,2),(1,2),(2,2)],
    # Diagonales
    [(0,0),(1,1),(2,2)],
    [(0,2),(1,1),(2,0)],
]


# ------------------------------------------------------------------
# Vérification de victoire dans une grille 3x3
# ------------------------------------------------------------------

def _check_winner_3x3(grid):
    """
    Vérifie si un joueur a gagné dans une grille 3x3 quelconque.

    Paramètres
    ----------
    grid : list[list[int]]  — grille 3x3 de valeurs (EMPTY, PLAYER_X, PLAYER_O)

    Retourne
    --------
    PLAYER_X | PLAYER_O si victoire, EMPTY sinon.
    """
    for line in WINNING_LINES:
        vals = [grid[r][c] for r, c in line]
        if vals[0] != EMPTY and vals[0] == vals[1] == vals[2]:
            return vals[0]
    return EMPTY


def _is_full_3x3(grid):
    """Vrai si toutes les cases de la grille 3x3 sont occupées."""
    return all(grid[r][c] != EMPTY for r in range(3) for c in range(3))


# ------------------------------------------------------------------
# Actions(s) — coups légaux
# ------------------------------------------------------------------

def get_legal_moves(board):
    """
    Retourne la liste de tous les coups légaux depuis l'état `board`.

    Un coup est (gr, gc, lr, lc).

    Règles :
    - Si board.active_grid est défini, on ne joue que dans cette sous-grille
      (si elle n'est pas terminée, sinon on est libre).
    - On ne peut jouer que dans les cases EMPTY des sous-grilles non terminées.
    - Si la partie est terminée, retourne [].

    Retourne
    --------
    list[tuple[int,int,int,int]]
    """
    if board.is_terminal():
        return []

    moves = []
    ag = board.active_grid

    # Déterminer les sous-grilles jouables
    if ag is not None and not board.is_subgrid_done(ag[0], ag[1]):
        candidate_grids = [ag]
    else:
        # Libre : toutes les sous-grilles non terminées
        candidate_grids = [
            (gr, gc)
            for gr in range(3)
            for gc in range(3)
            if not board.is_subgrid_done(gr, gc)
        ]

    for gr, gc in candidate_grids:
        for lr in range(3):
            for lc in range(3):
                if board.cells[gr][gc][lr][lc] == EMPTY:
                    moves.append((gr, gc, lr, lc))

    return moves


# ------------------------------------------------------------------
# Result(s, a) — application d'un coup
# ------------------------------------------------------------------

def apply_move(board, move):
    """
    Applique le coup `move` sur une COPIE de `board` et la retourne.

    Le plateau original n'est pas modifié (important pour Minimax).

    Paramètres
    ----------
    board : Board
    move  : tuple(gr, gc, lr, lc)

    Retourne
    --------
    Board  — nouvel état après le coup
    """
    gr, gc, lr, lc = move
    new_board = board.copy()

    # Placer le symbole du joueur courant
    new_board.cells[gr][gc][lr][lc] = board.current_player
    new_board.move_count += 1

    # Vérifier si la sous-grille (gr, gc) est maintenant gagnée ou nulle
    _update_local_winner(new_board, gr, gc)

    # Vérifier si la partie globale est terminée
    _update_global_winner(new_board)

    # Calculer la prochaine sous-grille active
    if not new_board.is_terminal():
        target = (lr, lc)
        if new_board.is_subgrid_done(target[0], target[1]):
            new_board.active_grid = None   # libre
        else:
            new_board.active_grid = target
    else:
        new_board.active_grid = None

    # Passer au joueur suivant
    new_board.current_player = board.opponent()

    return new_board


# ------------------------------------------------------------------
# Mise à jour locale
# ------------------------------------------------------------------

def _update_local_winner(board, gr, gc):
    """Met à jour board.local_winner[gr][gc] après un coup dans (gr, gc)."""
    if board.local_winner[gr][gc] != EMPTY:
        return  # déjà terminée

    local_grid = board.cells[gr][gc]
    winner = _check_winner_3x3(local_grid)

    if winner != EMPTY:
        board.local_winner[gr][gc] = winner
    elif _is_full_3x3(local_grid):
        board.local_winner[gr][gc] = DRAW


# ------------------------------------------------------------------
# Mise à jour globale
# ------------------------------------------------------------------

def _update_global_winner(board):
    """
    Met à jour board.global_winner en traitant la grille des vainqueurs
    locaux comme une grille 3x3 classique.

    Une sous-grille nulle (DRAW) ne compte ni pour X ni pour O.
    """
    if board.global_winner != EMPTY:
        return

    # Construire une grille 3x3 des vainqueurs locaux
    # (DRAW est traité comme EMPTY pour la victoire globale)
    meta = [
        [board.local_winner[gr][gc] if board.local_winner[gr][gc] != DRAW else EMPTY
         for gc in range(3)]
        for gr in range(3)
    ]

    winner = _check_winner_3x3(meta)
    if winner != EMPTY:
        board.global_winner = winner
        return

    # Match nul global : toutes les sous-grilles sont terminées
    all_done = all(
        board.local_winner[gr][gc] != EMPTY
        for gr in range(3) for gc in range(3)
    )
    if all_done:
        board.global_winner = DRAW


# ------------------------------------------------------------------
# Helpers publics
# ------------------------------------------------------------------

def check_local_win(board, gr, gc):
    """Retourne le vainqueur de la sous-grille (gr, gc) ou EMPTY."""
    return board.local_winner[gr][gc]


def check_global_win(board):
    """Retourne le vainqueur global ou EMPTY si la partie continue."""
    return board.global_winner


def is_draw(board):
    """Vrai si la partie est un match nul global."""
    return board.global_winner == DRAW