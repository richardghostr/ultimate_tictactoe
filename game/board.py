"""
board.py — Représentation de l'état du jeu Ultimate Tic Tac Toe.

Grille globale : 3x3 de sous-grilles.
Chaque sous-grille : 3x3 de cases.
Coordonnées : (global_row, global_col, local_row, local_col) — toutes en 0..2.
Joueurs : 1 = X (croix), 2 = O (ronds).
"""

EMPTY = 0
PLAYER_X = 1   # croix, joueur 1
PLAYER_O = 2   # ronds, joueur 2
DRAW = 3       # match nul local


class Board:
    """
    État complet d'une partie d'Ultimate Tic Tac Toe.

    Attributs
    ---------
    cells : list[list[list[list[int]]]]
        cells[gr][gc][lr][lc] = EMPTY | PLAYER_X | PLAYER_O
        gr, gc : indices de la sous-grille dans la grille globale (0..2)
        lr, lc : indices de la case dans la sous-grille (0..2)

    local_winner : list[list[int]]
        local_winner[gr][gc] = EMPTY | PLAYER_X | PLAYER_O | DRAW
        Résultat de chaque sous-grille.

    active_grid : tuple(int,int) | None
        Sous-grille où le prochain joueur DOIT jouer.
        None = le joueur peut choisir n'importe quelle sous-grille non terminée.

    current_player : int
        Joueur dont c'est le tour (PLAYER_X ou PLAYER_O).

    global_winner : int
        EMPTY si la partie n'est pas terminée,
        PLAYER_X | PLAYER_O si victoire globale,
        DRAW si match nul global.

    move_count : int
        Nombre de coups joués depuis le début.
    """

    def __init__(self):
        # Grille 9x9 représentée comme 3x3 de sous-grilles 3x3
        self.cells = [[[[EMPTY]*3 for _ in range(3)]
                        for _ in range(3)]
                       for _ in range(3)]

        # Résultats locaux des 9 sous-grilles
        self.local_winner = [[EMPTY]*3 for _ in range(3)]

        # Sous-grille active (None = libre)
        self.active_grid = None

        # Le joueur X commence toujours
        self.current_player = PLAYER_X

        # Résultat global de la partie
        self.global_winner = EMPTY

        # Compteur de coups
        self.move_count = 0

    # ------------------------------------------------------------------
    # Copie profonde (nécessaire pour Minimax sans modifier l'état réel)
    # ------------------------------------------------------------------

    def copy(self):
        """Retourne une copie indépendante du plateau."""
        new = Board.__new__(Board)

        new.cells = [
            [
                [[self.cells[gr][gc][lr][lc] for lc in range(3)]
                 for lr in range(3)]
                for gc in range(3)
            ]
            for gr in range(3)
        ]

        new.local_winner = [row[:] for row in self.local_winner]
        new.active_grid = self.active_grid
        new.current_player = self.current_player
        new.global_winner = self.global_winner
        new.move_count = self.move_count

        return new

    # ------------------------------------------------------------------
    # Helpers for local/global winner detection (used by in-place moves)
    # ------------------------------------------------------------------

    @staticmethod
    def _winning_lines():
        return [
            [(0,0),(0,1),(0,2)],
            [(1,0),(1,1),(1,2)],
            [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)],
            [(0,1),(1,1),(2,1)],
            [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)],
            [(0,2),(1,1),(2,0)],
        ]

    @staticmethod
    def _check_winner_3x3(grid):
        for line in Board._winning_lines():
            vals = [grid[r][c] for r, c in line]
            if vals[0] != EMPTY and vals[0] == vals[1] == vals[2]:
                return vals[0]
        return EMPTY

    @staticmethod
    def _is_full_3x3(grid):
        return all(grid[r][c] != EMPTY for r in range(3) for c in range(3))

    def _update_local_and_global_after_move(self, gr, gc):
        # Update local winner for the subgrid (gr,gc)
        if self.local_winner[gr][gc] == EMPTY:
            local_grid = self.cells[gr][gc]
            winner = Board._check_winner_3x3(local_grid)
            if winner != EMPTY:
                self.local_winner[gr][gc] = winner
            elif Board._is_full_3x3(local_grid):
                self.local_winner[gr][gc] = DRAW

        # Update global winner
        if self.global_winner == EMPTY:
            meta = [
                [self.local_winner[r][c] if self.local_winner[r][c] != DRAW else EMPTY
                 for c in range(3)]
                for r in range(3)
            ]
            winner = Board._check_winner_3x3(meta)
            if winner != EMPTY:
                self.global_winner = winner
                return
            all_done = all(self.local_winner[r][c] != EMPTY for r in range(3) for c in range(3))
            if all_done:
                self.global_winner = DRAW

    # ------------------------------------------------------------------
    # In-place move application / undo
    # ------------------------------------------------------------------

    def make_move(self, move):
        """Applique `move` en place et retourne un objet undo.

        L'objet retourné contient les informations nécessaires pour annuler
        le coup via `undo_move(undo_obj)`.
        """
        gr, gc, lr, lc = move

        prev_cell = self.cells[gr][gc][lr][lc]
        if prev_cell != EMPTY:
            raise ValueError("make_move: case déjà occupée")

        prev_local = self.local_winner[gr][gc]
        prev_global = self.global_winner
        prev_active = self.active_grid
        prev_player = self.current_player
        prev_move_count = self.move_count

        # Apply
        self.cells[gr][gc][lr][lc] = self.current_player
        self.move_count += 1

        # Update local/global winners and compute next active grid
        self._update_local_and_global_after_move(gr, gc)

        if not self.is_terminal():
            target = (lr, lc)
            if self.is_subgrid_done(target[0], target[1]):
                self.active_grid = None
            else:
                self.active_grid = target
        else:
            self.active_grid = None

        # Switch player
        self.current_player = self.opponent(prev_player)

        undo = (move, prev_local, prev_global, prev_active, prev_player, prev_move_count)
        return undo

    def undo_move(self, undo_obj):
        """Annule un coup appliqué par `make_move` en restaurant l'état."""
        (gr, gc, lr, lc), prev_local, prev_global, prev_active, prev_player, prev_move_count = undo_obj

        # Clear the cell
        self.cells[gr][gc][lr][lc] = EMPTY

        # Restore state
        self.local_winner[gr][gc] = prev_local
        self.global_winner = prev_global
        self.active_grid = prev_active
        self.current_player = prev_player
        self.move_count = prev_move_count

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def opponent(self, player=None):
        """Retourne l'adversaire du joueur donné (ou du joueur courant)."""
        p = player if player is not None else self.current_player
        return PLAYER_O if p == PLAYER_X else PLAYER_X

    def is_terminal(self):
        """Vrai si la partie est terminée (victoire globale ou match nul)."""
        return self.global_winner != EMPTY

    def is_subgrid_done(self, gr, gc):
        """Vrai si la sous-grille (gr, gc) est terminée (gagnée ou nulle)."""
        return self.local_winner[gr][gc] != EMPTY

    def __repr__(self):
        return (
            f"Board(player={self.current_player}, "
            f"active={self.active_grid}, "
            f"winner={self.global_winner}, "
            f"moves={self.move_count})"
        )