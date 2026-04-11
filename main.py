"""
main.py — Point d'entrée du projet Ultimate Tic Tac Toe.

Modes disponibles :
    1. Humain vs IA
    2. IA vs Humain
    3. IA vs IA  (combat automatique, 2 parties)
    4. Humain vs Humain

Usage :
    python main.py                        # menu interactif
    python main.py --mode ai_vs_ai        # combat IA direct
    python main.py --mode human_vs_ai     # humain contre IA
    python main.py --depth1 4 --depth2 3  # profondeurs personnalisées
"""

import argparse
import sys

from game.board import PLAYER_X, PLAYER_O, DRAW
from game.game import Game
from ai.player import HumanPlayer, AIPlayer


# ------------------------------------------------------------------
# Scoring DVO (barème du projet)
# ------------------------------------------------------------------
# Victoire rapide : 4 pts | Victoire lente : 3 pts
# Nul rapide     : 1 pt  | Nul lent       : 0 pt
# Défaite rapide : 1 pt  | Défaite lente  : 0 pt
# "Rapide" = parmi les 2 plus courts résultats de la même catégorie

RAPID_THRESHOLD = 50   # coups — partie "rapide" si move_count <= seuil


def score_result(result, move_count, player_id, rapid=True):
    """
    Retourne les points DVO pour un résultat donné.

    Paramètres
    ----------
    result    : PLAYER_X | PLAYER_O | DRAW
    move_count: int
    player_id : PLAYER_X | PLAYER_O  — point de vue du joueur
    rapid     : bool — True si la partie est "rapide"
    """
    if result == player_id:       # Victoire
        return 4 if rapid else 3
    elif result == DRAW:
        return 1 if rapid else 0
    else:                          # Défaite
        return 1 if rapid else 0


# ------------------------------------------------------------------
# Modes de jeu
# ------------------------------------------------------------------

def play_human_vs_ai(depth=4, human_first=True):
    """Lance une partie Humain vs IA."""
    human = HumanPlayer("Vous")
    ai = AIPlayer("IA", depth=depth)

    if human_first:
        game = Game(human, ai)
    else:
        game = Game(ai, human)

    return game.run()


def play_ai_vs_ai(depth1=4, depth2=3, show=True, time_limit=None):
    """
    Lance deux parties IA vs IA (chacune commence une fois).
    Affiche le score DVO final.
    """
    ia1 = AIPlayer("IA-1", depth=depth1, time_limit=time_limit)
    ia2 = AIPlayer("IA-2", depth=depth2, time_limit=time_limit)

    total_moves = []
    results = []

    print("\n" + "="*50)
    print("  COMBAT IA vs IA — Partie 1 (IA-1 commence)")
    print("="*50)
    g1 = Game(ia1, ia2, show_board=show)
    r1 = g1.run()
    stats1 = g1.get_stats()
    total_moves.append(stats1['move_count'])
    results.append((r1, stats1['move_count'], PLAYER_X))   # IA-1 = X

    print("\n" + "="*50)
    print("  COMBAT IA vs IA — Partie 2 (IA-2 commence)")
    print("="*50)
    g2 = Game(ia2, ia1, show_board=show)
    r2 = g2.run()
    stats2 = g2.get_stats()
    total_moves.append(stats2['move_count'])
    results.append((r2, stats2['move_count'], PLAYER_O))   # IA-1 = O dans partie 2

    # Calcul du score DVO
    threshold = sum(total_moves) / len(total_moves)
    score_ia1 = 0
    score_ia2 = 0

    for i, (result, moves, ia1_side) in enumerate(results):
        rapid = moves <= threshold
        s1 = score_result(result, moves, ia1_side, rapid)
        ia2_side = PLAYER_O if ia1_side == PLAYER_X else PLAYER_X
        s2 = score_result(result, moves, ia2_side, rapid)
        score_ia1 += s1
        score_ia2 += s2
        print(f"  Partie {i+1} : {'rapide' if rapid else 'lente'} "
              f"({moves} coups) | IA-1: +{s1}pts | IA-2: +{s2}pts")

    print(f"\n  SCORE FINAL : IA-1 = {score_ia1}pts | IA-2 = {score_ia2}pts")

    return score_ia1, score_ia2


def play_human_vs_human():
    """Lance une partie Humain vs Humain."""
    p1 = HumanPlayer("Joueur 1 (X)")
    p2 = HumanPlayer("Joueur 2 (O)")
    game = Game(p1, p2)
    return game.run()


# ------------------------------------------------------------------
# Menu interactif
# ------------------------------------------------------------------

def interactive_menu():
    print("\n" + "="*50)
    print("   ULTIMATE TIC TAC TOE — IA Minimax Alpha-Beta")
    print("="*50)
    print("  1. Humain (X) vs IA (O)")
    print("  2. IA (X) vs Humain (O)")
    print("  3. IA vs IA  (combat automatique)")
    print("  4. Humain vs Humain")
    print("  5. Quitter")
    print("="*50)

    choice = input("  Votre choix : ").strip()

    if choice == "1":
        depth = _ask_depth()
        play_human_vs_ai(depth=depth, human_first=True)

    elif choice == "2":
        depth = _ask_depth()
        play_human_vs_ai(depth=depth, human_first=False)

    elif choice == "3":
        print("\n  Profondeur IA-1 (défaut 4) :", end=" ")
        try:
            d1 = int(input().strip() or "4")
        except ValueError:
            d1 = 4
        print("  Profondeur IA-2 (défaut 3) :", end=" ")
        try:
            d2 = int(input().strip() or "3")
        except ValueError:
            d2 = 3
        show = input("  Afficher le plateau ? (o/N) : ").strip().lower() == 'o'
        play_ai_vs_ai(depth1=d1, depth2=d2, show=show)

    elif choice == "4":
        play_human_vs_human()

    elif choice == "5":
        print("  Au revoir !")
        sys.exit(0)

    else:
        print("  Choix invalide.")


def _ask_depth():
    print("  Profondeur de l'IA (1-8, défaut 4) :", end=" ")
    try:
        d = int(input().strip() or "4")
        return max(1, min(8, d))
    except ValueError:
        return 4


# ------------------------------------------------------------------
# Point d'entrée CLI
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Tic Tac Toe — IA Minimax Alpha-Beta"
    )
    parser.add_argument(
        "--mode",
        choices=["human_vs_ai", "ai_vs_human", "ai_vs_ai", "human_vs_human"],
        default=None,
        help="Mode de jeu"
    )
    parser.add_argument("--depth1", type=int, default=4, help="Profondeur IA-1 (défaut 4)")
    parser.add_argument("--depth2", type=int, default=3, help="Profondeur IA-2 (défaut 3)")
    parser.add_argument("--no-display", action="store_true", help="Désactiver l'affichage (IA vs IA)")
    parser.add_argument("--time-limit", type=float, default=None,
                        help="Limite de temps par coup en secondes (approfondissement itératif)")

    args = parser.parse_args()

    if args.mode is None:
        # Menu interactif
        while True:
            interactive_menu()

    elif args.mode == "human_vs_ai":
        play_human_vs_ai(depth=args.depth1, human_first=True)

    elif args.mode == "ai_vs_human":
        play_human_vs_ai(depth=args.depth1, human_first=False)

    elif args.mode == "ai_vs_ai":
        play_ai_vs_ai(
            depth1=args.depth1,
            depth2=args.depth2,
            show=not args.no_display,
            time_limit=args.time_limit
        )

    elif args.mode == "human_vs_human":
        play_human_vs_human()


if __name__ == "__main__":
    main()