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