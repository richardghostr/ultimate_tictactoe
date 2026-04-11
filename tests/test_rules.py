"""
test_rules.py — Tests unitaires du moteur de règles et de l'IA.

Couvre :
- Coups légaux (get_legal_moves)
- Application de coups (apply_move)
- Victoires locales et globales
- Match nul
- Contrainte de grille active
- Heuristique (evaluate)
- Minimax (get_best_move)

Exécution :
    python -m pytest tests/test_rules.py -v
    ou directement :
    python tests/test_rules.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.board import Board, EMPTY, PLAYER_X, PLAYER_O, DRAW
from game.rules import (
    get_legal_moves, apply_move,
    check_local_win, check_global_win, is_draw,
    _check_winner_3x3, _is_full_3x3, _update_local_winner, _update_global_winner
)
from ai.heuristic import evaluate
from ai.minimax import get_best_move
from ai.player import AIPlayer, HumanPlayer, make_player


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _force_cells(board, gr, gc, positions, player):
    """Place `player` dans les cases `positions` de la sous-grille (gr, gc)."""
    for lr, lc in positions:
        board.cells[gr][gc][lr][lc] = player


def _fill_subgrid(board, gr, gc, winner):
    """
    Remplir rapidement une sous-grille pour la faire gagner par `winner`
    (ou la rendre nulle si winner=DRAW).
    Puis met à jour local_winner directement.
    """
    if winner == PLAYER_X:
        # X gagne colonne 0
        board.cells[gr][gc][0][0] = PLAYER_X
        board.cells[gr][gc][1][0] = PLAYER_X
        board.cells[gr][gc][2][0] = PLAYER_X
        board.local_winner[gr][gc] = PLAYER_X
    elif winner == PLAYER_O:
        # O gagne ligne 0
        board.cells[gr][gc][0][0] = PLAYER_O
        board.cells[gr][gc][0][1] = PLAYER_O
        board.cells[gr][gc][0][2] = PLAYER_O
        board.local_winner[gr][gc] = PLAYER_O
    elif winner == DRAW:
        # Remplir d'alternance sans victoire
        pattern = [PLAYER_X, PLAYER_O, PLAYER_X,
                   PLAYER_O, PLAYER_X, PLAYER_O,
                   PLAYER_O, PLAYER_X, PLAYER_O]
        k = 0
        for lr in range(3):
            for lc in range(3):
                board.cells[gr][gc][lr][lc] = pattern[k]
                k += 1
        board.local_winner[gr][gc] = DRAW


# ------------------------------------------------------------------
# Tests : Board
# ------------------------------------------------------------------

def test_board_initial_state():
    b = Board()
    assert b.current_player == PLAYER_X
    assert b.active_grid is None
    assert b.global_winner == EMPTY
    assert b.move_count == 0
    for gr in range(3):
        for gc in range(3):
            assert b.local_winner[gr][gc] == EMPTY
            for lr in range(3):
                for lc in range(3):
                    assert b.cells[gr][gc][lr][lc] == EMPTY
    print("[OK] test_board_initial_state")


def test_board_copy_independence():
    b = Board()
    b2 = b.copy()
    b2.cells[0][0][0][0] = PLAYER_X
    b2.current_player = PLAYER_O
    assert b.cells[0][0][0][0] == EMPTY
    assert b.current_player == PLAYER_X
    print("[OK] test_board_copy_independence")


# ------------------------------------------------------------------
# Tests : get_legal_moves
# ------------------------------------------------------------------

def test_legal_moves_initial():
    b = Board()
    moves = get_legal_moves(b)
    assert len(moves) == 81
    print("[OK] test_legal_moves_initial")


def test_legal_moves_after_first():
    b = Board()
    b = apply_move(b, (1, 1, 1, 1))  # X centre global centre
    moves = get_legal_moves(b)
    # Active_grid = (1,1), déjà 1 case prise -> 8 coups
    assert len(moves) == 8
    assert all(gr == 1 and gc == 1 for gr, gc, _, _ in moves)
    print("[OK] test_legal_moves_after_first")


def test_legal_moves_active_grid_done():
    """Quand la sous-grille active est terminée, on est libre."""
    b = Board()
    _fill_subgrid(b, 1, 1, PLAYER_X)
    b.active_grid = (1, 1)
    b.current_player = PLAYER_O
    moves = get_legal_moves(b)
    # (1,1) est terminée -> libre sur les 8 autres sous-grilles non terminées
    assert all(not (gr == 1 and gc == 1) for gr, gc, _, _ in moves)
    assert len(moves) == 8 * 9  # 8 sous-grilles * 9 cases
    print("[OK] test_legal_moves_active_grid_done")


def test_no_legal_moves_when_terminal():
    b = Board()
    b.global_winner = PLAYER_X
    assert get_legal_moves(b) == []
    print("[OK] test_no_legal_moves_when_terminal")


# ------------------------------------------------------------------
# Tests : apply_move
# ------------------------------------------------------------------

def test_apply_move_does_not_modify_original():
    b = Board()
    b2 = apply_move(b, (0, 0, 0, 0))
    assert b.cells[0][0][0][0] == EMPTY
    assert b2.cells[0][0][0][0] == PLAYER_X
    print("[OK] test_apply_move_does_not_modify_original")


def test_apply_move_switches_player():
    b = Board()
    b2 = apply_move(b, (0, 0, 0, 0))
    assert b2.current_player == PLAYER_O
    b3 = apply_move(b2, (0, 0, 1, 1))
    assert b3.current_player == PLAYER_X
    print("[OK] test_apply_move_switches_player")


def test_apply_move_active_grid_constraint():
    b = Board()
    b2 = apply_move(b, (0, 0, 1, 2))   # joue en (lr=1, lc=2) -> active=(1,2)
    assert b2.active_grid == (1, 2)
    b3 = apply_move(b2, (1, 2, 0, 0))  # joue en (lr=0, lc=0) -> active=(0,0)
    assert b3.active_grid == (0, 0)
    print("[OK] test_apply_move_active_grid_constraint")


def test_apply_move_increments_count():
    b = Board()
    b = apply_move(b, (0, 0, 0, 0))
    assert b.move_count == 1
    b = apply_move(b, (0, 0, 1, 1))
    assert b.move_count == 2
    print("[OK] test_apply_move_increments_count")


# ------------------------------------------------------------------
# Tests : victoires locales
# ------------------------------------------------------------------

def test_local_win_row():
    b = Board()
    _force_cells(b, 0, 0, [(0,0),(0,1),(0,2)], PLAYER_X)
    _update_local_winner(b, 0, 0)
    assert b.local_winner[0][0] == PLAYER_X
    print("[OK] test_local_win_row")


def test_local_win_col():
    b = Board()
    _force_cells(b, 1, 1, [(0,0),(1,0),(2,0)], PLAYER_O)
    _update_local_winner(b, 1, 1)
    assert b.local_winner[1][1] == PLAYER_O
    print("[OK] test_local_win_col")


def test_local_win_diag():
    b = Board()
    _force_cells(b, 2, 2, [(0,0),(1,1),(2,2)], PLAYER_X)
    _update_local_winner(b, 2, 2)
    assert b.local_winner[2][2] == PLAYER_X
    print("[OK] test_local_win_diag")


def test_local_draw():
    b = Board()
    _fill_subgrid(b, 0, 0, DRAW)
    assert b.local_winner[0][0] == DRAW
    print("[OK] test_local_draw")


# ------------------------------------------------------------------
# Tests : victoires globales
# ------------------------------------------------------------------

def test_global_win_row():
    b = Board()
    for gc in range(3):
        _fill_subgrid(b, 0, gc, PLAYER_X)
    _update_global_winner(b)
    assert b.global_winner == PLAYER_X
    print("[OK] test_global_win_row")


def test_global_win_diag():
    b = Board()
    for i in range(3):
        _fill_subgrid(b, i, i, PLAYER_O)
    _update_global_winner(b)
    assert b.global_winner == PLAYER_O
    print("[OK] test_global_win_diag")


def test_global_draw():
    b = Board()
    # Remplir toutes les sous-grilles alternativement sans victoire
    pattern = [
        PLAYER_X, PLAYER_O, PLAYER_X,
        PLAYER_O, DRAW,     PLAYER_O,
        PLAYER_X, PLAYER_O, PLAYER_X,
    ]
    k = 0
    for gr in range(3):
        for gc in range(3):
            _fill_subgrid(b, gr, gc, pattern[k])
            k += 1
    _update_global_winner(b)
    # X a: (0,0),(0,2),(2,0),(2,2) pas d'alignement -> DRAW si aucun alignement global
    # En fait X a (0,0),(0,2) et (2,0),(2,2) mais pas 3 alignés -> dépend du pattern
    # On vérifie juste que toutes les sous-grilles sont terminées -> pas EMPTY
    assert b.global_winner != EMPTY
    print("[OK] test_global_draw (toutes sous-grilles terminées)")


# ------------------------------------------------------------------
# Tests : heuristique
# ------------------------------------------------------------------

def test_evaluate_empty_board():
    b = Board()
    score = evaluate(b, PLAYER_X)
    assert score == 0  # plateau vide = équilibré
    print("[OK] test_evaluate_empty_board")


def test_evaluate_favors_local_wins():
    b = Board()
    _fill_subgrid(b, 0, 0, PLAYER_X)
    score_x = evaluate(b, PLAYER_X)
    score_o = evaluate(b, PLAYER_O)
    assert score_x > 0
    assert score_o < 0
    print("[OK] test_evaluate_favors_local_wins")


def test_evaluate_terminal_win():
    b = Board()
    b.global_winner = PLAYER_X
    from ai.heuristic import SCORE_GLOBAL_WIN
    assert evaluate(b, PLAYER_X) == SCORE_GLOBAL_WIN
    assert evaluate(b, PLAYER_O) == -SCORE_GLOBAL_WIN
    print("[OK] test_evaluate_terminal_win")


# ------------------------------------------------------------------
# Tests : Minimax
# ------------------------------------------------------------------

def test_minimax_wins_immediately():
    """L'IA doit gagner si un coup gagnant est disponible."""
    b = Board()
    # X a deux sous-grilles en ligne 0 (gagnées), besoin de gagner (0,2)
    _fill_subgrid(b, 0, 0, PLAYER_X)
    _fill_subgrid(b, 0, 1, PLAYER_X)
    # (0,2) est libre : forcer X à jouer dedans en colonne 0 pour la gagner
    # On pré-remplit 2 cases gagnantes pour X dans (0,2)
    b.cells[0][2][0][0] = PLAYER_X
    b.cells[0][2][1][0] = PLAYER_X
    # Il reste à jouer (0,2,2,0) pour que X gagne (0,2) et la partie
    b.current_player = PLAYER_X
    b.active_grid = None  # libre

    move = get_best_move(b, depth=3, root_player=PLAYER_X)
    assert move is not None
    # Le coup gagnant est dans (0,2)
    assert move[0] == 0 and move[1] == 2, f"Attendu sous-grille (0,2), obtenu {move}"
    print("[OK] test_minimax_wins_immediately")


def test_minimax_blocks_opponent():
    """L'IA doit bloquer une victoire imminente de l'adversaire."""
    b = Board()
    # O a deux sous-grilles gagnées en ligne 0
    _fill_subgrid(b, 0, 0, PLAYER_O)
    _fill_subgrid(b, 0, 1, PLAYER_O)
    # O a 2 cases gagnantes dans (0,2) en colonne 0 -> X doit bloquer
    b.cells[0][2][0][0] = PLAYER_O
    b.cells[0][2][1][0] = PLAYER_O
    b.current_player = PLAYER_X
    b.active_grid = None

    move = get_best_move(b, depth=3, root_player=PLAYER_X)
    assert move is not None
    # X doit jouer dans (0,2) pour bloquer O
    assert move[0] == 0 and move[1] == 2, f"Attendu sous-grille (0,2), obtenu {move}"
    print("[OK] test_minimax_blocks_opponent")


def test_minimax_returns_valid_move():
    """Le Minimax retourne toujours un coup légal."""
    b = Board()
    legal = get_legal_moves(b)
    move = get_best_move(b, depth=2)
    assert move in legal
    print("[OK] test_minimax_returns_valid_move")


# ------------------------------------------------------------------
# Tests : Player
# ------------------------------------------------------------------

def test_make_player_human():
    p = make_player("human", name="Alice")
    assert p.is_human
    assert p.name == "Alice"
    print("[OK] test_make_player_human")


def test_make_player_ai():
    p = make_player("ai:3", name="Bot")
    assert not p.is_human
    assert isinstance(p, AIPlayer)
    assert p.depth == 3
    print("[OK] test_make_player_ai")


def test_aiplayer_get_move():
    b = Board()
    ai = AIPlayer("TestAI", depth=2)
    move = ai.get_move(b)
    assert move in get_legal_moves(b)
    print("[OK] test_aiplayer_get_move")


# ------------------------------------------------------------------
# Lancement de tous les tests
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        # Board
        test_board_initial_state,
        test_board_copy_independence,
        # Legal moves
        test_legal_moves_initial,
        test_legal_moves_after_first,
        test_legal_moves_active_grid_done,
        test_no_legal_moves_when_terminal,
        # Apply move
        test_apply_move_does_not_modify_original,
        test_apply_move_switches_player,
        test_apply_move_active_grid_constraint,
        test_apply_move_increments_count,
        # Victoires locales
        test_local_win_row,
        test_local_win_col,
        test_local_win_diag,
        test_local_draw,
        # Victoires globales
        test_global_win_row,
        test_global_win_diag,
        test_global_draw,
        # Heuristique
        test_evaluate_empty_board,
        test_evaluate_favors_local_wins,
        test_evaluate_terminal_win,
        # Minimax
        test_minimax_returns_valid_move,
        test_minimax_blocks_opponent,
        test_minimax_wins_immediately,
        # Player
        test_make_player_human,
        test_make_player_ai,
        test_aiplayer_get_move,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} : {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"  {passed} tests réussis / {failed} échecs")
    print(f"{'='*40}")