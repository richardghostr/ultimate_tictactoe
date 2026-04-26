"""
game.py — Boucle principale de la partie Ultimate Tic Tac Toe.

Gère l'alternance des tours entre deux joueurs (humain ou IA),
l'affichage, la saisie et la détection de fin de partie.

Utilisation :
    from game.game import Game
    g = Game(player1, player2)   # player1 = X, player2 = O
    g.run()
"""

import time
from .board import Board, PLAYER_X, PLAYER_O, DRAW
from .rules import get_legal_moves, apply_move
from .display import (
    display_board, display_move_prompt,
    display_ai_thinking, display_ai_move, parse_human_move
)
from .clock import GameTimer


class Game:
    """
    Contrôleur d'une partie complète.

    Paramètres
    ----------
    player_x : Player  — joueur qui joue X (croix), commence en premier
    player_o : Player  — joueur qui joue O (ronds)
    show_board : bool  — afficher le plateau après chaque coup (défaut True)
    time_limit : float — secondes max par coup pour l'IA (défaut None = pas de limite)
    """

    def __init__(self, player_x, player_o, show_board=True, time_limit=None):
        self.player_x = player_x
        self.player_o = player_o
        self.show_board = show_board
        self.time_limit = time_limit

        self.board = Board()
        self.history = []     # liste des coups joués
        self.timings = []     # durées par coup (pour les stats)
        # per-player timings
        self.per_player_timings = {PLAYER_X: [], PLAYER_O: []}
        # game timer (total + per-player clocks)
        self.timer = GameTimer()

    def run(self):
        """
        Lance la boucle principale.

        Retourne
        --------
        int — PLAYER_X, PLAYER_O ou DRAW
        """
        if self.show_board:
            print("\n=== Ultimate Tic Tac Toe ===")
            print(f"  {self.player_x.name} (X) vs {self.player_o.name} (O)\n")
            display_board(self.board, timer=self.timer)

        last_move = None

        # démarrer le chronométrage total et celui du joueur X (qui commence)
        self.timer.start_total()
        self.timer.start_for(self.board.current_player)

        while not self.board.is_terminal():
            current = self._current_player_obj()

            # Obtenir le coup (on démarre l'horloge du joueur courant si nécessaire)
            self.timer.start_for(self.board.current_player)
            start = time.time()
            move = self._get_move(current)
            elapsed = time.time() - start

            # Stopper l'horloge du joueur courant aussitôt qu'il a joué
            self.timer.stop_for(current_player := self.board.current_player)

            if move is None:
                # Ne devrait pas arriver si tout est correct
                break

            self.history.append(move)
            self.timings.append(elapsed)
            self.per_player_timings[current_player].append(elapsed)

            # Appliquer le coup
            self.board = apply_move(self.board, move)
            last_move = move

            # Lorsque le prochain joueur prend la main, démarrer sa montre
            if not self.board.is_terminal():
                self.timer.switch_to(self.board.current_player)

            # Affichage
                if self.show_board:
                    if current.is_human:
                        pass  # le plateau a déjà été affiché avant la saisie
                    else:
                        display_ai_move(move)
                    display_board(self.board, last_move=last_move, timer=self.timer)

        # Fin de partie
        result = self.board.global_winner
        # Stopper toutes les montres et le chronomètre total
        self.timer.stop_all()

        if self.show_board:
            self._display_result(result)

        return result

    # ------------------------------------------------------------------
    # Helpers internes
    # ------------------------------------------------------------------

    def _current_player_obj(self):
        """Retourne l'objet joueur dont c'est le tour."""
        if self.board.current_player == PLAYER_X:
            return self.player_x
        return self.player_o

    def _get_move(self, player):
        """
        Demande un coup au joueur (humain ou IA).
        Pour un humain, boucle jusqu'à une saisie valide.
        Pour une IA, affiche un message de réflexion.
        """
        if player.is_human:
            if self.show_board:
                display_move_prompt(self.board)
            while True:
                try:
                    raw = input("  > ")
                except (EOFError, KeyboardInterrupt):
                    print("\nPartie interrompue.")
                    return None
                move = parse_human_move(raw, self.board)
                if move is not None:
                    return move
        else:
            if self.show_board:
                display_ai_thinking()
            return player.get_move(self.board)

    def _display_result(self, result):
        """Affiche le résultat final de la partie."""
        print("\n" + "="*40)
        if result == DRAW:
            print("  RÉSULTAT : Match nul !")
        elif result == PLAYER_X:
            print(f"  RÉSULTAT : {self.player_x.name} (X) gagne !")
        elif result == PLAYER_O:
            print(f"  RÉSULTAT : {self.player_o.name} (O) gagne !")
        print(f"  Nombre de coups : {self.board.move_count}")

        total = self.timer.total_time()
        tx = self.timer.get_player_time(PLAYER_X)
        to = self.timer.get_player_time(PLAYER_O)
        moves_x = len(self.per_player_timings[PLAYER_X])
        moves_o = len(self.per_player_timings[PLAYER_O])
        avg_x = (sum(self.per_player_timings[PLAYER_X]) / moves_x) if moves_x else 0.0
        avg_o = (sum(self.per_player_timings[PLAYER_O]) / moves_o) if moves_o else 0.0

        print(f"  Temps total de la partie : {total:.3f}s")
        print(f"  Temps joueur X ({self.player_x.name}) : {tx:.3f}s — moy. par coup {avg_x:.3f}s")
        print(f"  Temps joueur O ({self.player_o.name}) : {to:.3f}s — moy. par coup {avg_o:.3f}s")
        print("="*40 + "\n")

    def get_stats(self):
        """
        Retourne un dictionnaire de statistiques sur la partie.

        Utilisé pour le scoring des combats IA vs IA.
        """
        total = self.timer.total_time()
        tx = self.timer.get_player_time(PLAYER_X)
        to = self.timer.get_player_time(PLAYER_O)
        moves_x = len(self.per_player_timings[PLAYER_X])
        moves_o = len(self.per_player_timings[PLAYER_O])
        return {
            'winner': self.board.global_winner,
            'move_count': self.board.move_count,
            'timings': self.timings,
            'avg_time': sum(self.timings) / len(self.timings) if self.timings else 0,
            'max_time': max(self.timings) if self.timings else 0,
            'history': self.history,
            'total_time': total,
            'time_x': tx,
            'time_o': to,
            'avg_time_x': (sum(self.per_player_timings[PLAYER_X]) / moves_x) if moves_x else 0,
            'avg_time_o': (sum(self.per_player_timings[PLAYER_O]) / moves_o) if moves_o else 0,
            'moves_x': moves_x,
            'moves_o': moves_o,
        }