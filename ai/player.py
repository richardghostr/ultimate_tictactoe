"""
player.py — Classes joueurs pour Ultimate Tic Tac Toe.

Deux types de joueurs partagent la même interface get_move(board) :
    HumanPlayer  — saisie au clavier (gérée par game.py)
    AIPlayer     — décision via Minimax Alpha-Beta

Cette abstraction permet de faire s'affronter deux IA simplement :
    ia1 = AIPlayer("IA-Défensive", depth=3)
    ia2 = AIPlayer("IA-Offensive", depth=4)
    game = Game(ia1, ia2)
"""

from ai.minimax import get_best_move, get_best_move_timed
from game.board import PLAYER_X, PLAYER_O


# ------------------------------------------------------------------
# Classe de base
# ------------------------------------------------------------------

class Player:
    """
    Interface commune pour tous les joueurs.

    Attributs
    ---------
    name     : str  — nom affiché
    is_human : bool — True si saisie humaine
    """

    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human

    def get_move(self, board):
        """
        Retourne le coup choisi : tuple(gr, gc, lr, lc).
        Pour HumanPlayer, la saisie est gérée par game.py (cette méthode n'est pas appelée).
        """
        raise NotImplementedError

    def __repr__(self):
        kind = "Humain" if self.is_human else "IA"
        return f"{kind}({self.name})"


# ------------------------------------------------------------------
# Joueur humain
# ------------------------------------------------------------------

class HumanPlayer(Player):
    """
    Joueur humain. La saisie est entièrement gérée par game.py
    via display.parse_human_move().
    Cette classe sert uniquement d'identifiant.
    """

    def __init__(self, name="Humain"):
        super().__init__(name, is_human=True)

    def get_move(self, board):
        # Ne devrait jamais être appelé directement
        raise RuntimeError("HumanPlayer.get_move() ne doit pas être appelé directement.")


# ------------------------------------------------------------------
# Joueur IA (Minimax + Alpha-Beta)
# ------------------------------------------------------------------

class AIPlayer(Player):
    """
    Joueur IA basé sur Minimax avec élagage Alpha-Beta.

    Paramètres
    ----------
    name       : str   — nom de l'IA
    depth      : int   — profondeur fixe de recherche (défaut 4)
    time_limit : float | None — si défini, utilise l'approfondissement
                               itératif avec limite de temps (en secondes)
    max_depth  : int   — profondeur max pour l'approfondissement itératif
    """

    def __init__(self, name="IA", depth=4, time_limit=None, max_depth=8):
        super().__init__(name, is_human=False)
        self.depth = depth
        self.time_limit = time_limit
        self.max_depth = max_depth

        # Statistiques internes
        self._move_count = 0
        self._total_time = 0.0

    def get_move(self, board):
        """
        Calcule et retourne le meilleur coup via Minimax Alpha-Beta.

        Retourne
        --------
        tuple(gr, gc, lr, lc)
        """
        import time
        start = time.time()

        if self.time_limit is not None:
            move = get_best_move_timed(
                board,
                time_limit=self.time_limit,
                max_depth=self.max_depth,
                root_player=board.current_player
            )
        else:
            move = get_best_move(
                board,
                depth=self.depth,
                root_player=board.current_player
            )

        elapsed = time.time() - start
        self._move_count += 1
        self._total_time += elapsed

        return move

    def avg_time(self):
        """Temps moyen par coup (secondes)."""
        if self._move_count == 0:
            return 0.0
        return self._total_time / self._move_count

    def reset_stats(self):
        """Remet les statistiques à zéro."""
        self._move_count = 0
        self._total_time = 0.0

    def __repr__(self):
        if self.time_limit:
            return f"IA({self.name}, timed={self.time_limit}s, max_depth={self.max_depth})"
        return f"IA({self.name}, depth={self.depth})"


# ------------------------------------------------------------------
# Factory : créer un joueur depuis une chaîne de config
# ------------------------------------------------------------------

def make_player(config, name=None):
    """
    Crée un joueur depuis une configuration simple.

    Paramètres
    ----------
    config : str | dict
        "human"            → HumanPlayer
        "ai"               → AIPlayer(depth=4)
        "ai:3"             → AIPlayer(depth=3)
        "ai:timed:5"       → AIPlayer(time_limit=5.0)
        dict avec clés     → AIPlayer(**config)

    name : str | None — nom du joueur (optionnel)

    Retourne
    --------
    Player
    """
    if isinstance(config, dict):
        kind = config.pop("type", "ai")
        n = config.pop("name", name or "IA")
        if kind == "human":
            return HumanPlayer(name=n)
        return AIPlayer(name=n, **config)

    config = str(config).strip().lower()

    if config == "human":
        return HumanPlayer(name=name or "Humain")

    if config.startswith("ai:timed:"):
        t = float(config.split(":")[2])
        return AIPlayer(name=name or "IA", time_limit=t)

    if config.startswith("ai:"):
        d = int(config.split(":")[1])
        return AIPlayer(name=name or "IA", depth=d)

    # Par défaut : IA profondeur 4
    return AIPlayer(name=name or "IA", depth=4)