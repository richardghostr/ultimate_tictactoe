"""
display.py — Affichage texte de la grille 9x9 d'Ultimate Tic Tac Toe.

Format d'affichage :
- Les colonnes et lignes sont numérotées de 1 à 9 (pour la saisie humaine).
- Les sous-grilles sont séparées par des doubles traits.
- La sous-grille active est mise en évidence avec des crochets [ ].
- Une sous-grille gagnée affiche un grand X ou O centré.
- Le joueur courant et l'état de la partie sont affichés en bas.
"""

from .board import Board, EMPTY, PLAYER_X, PLAYER_O, DRAW

# Symboles d'affichage
_SYM = {EMPTY: '.', PLAYER_X: 'X', PLAYER_O: 'O'}
_WIN_SYM = {PLAYER_X: 'X', PLAYER_O: 'O', DRAW: '='}

# Séparateurs
_SEP_INNER = '-'   # séparateur entre cases dans une sous-grille
_SEP_OUTER = '='   # séparateur entre sous-grilles


def display_board(board, last_move=None):
    """
    Affiche la grille complète dans le terminal.

    Paramètres
    ----------
    board     : Board  — état courant
    last_move : tuple(gr, gc, lr, lc) | None — dernier coup joué (surligné)
    """
    print()
    _print_col_header()
    print()

    for gr in range(3):
        # Séparateur entre groupes de sous-grilles (lignes globales)
        if gr > 0:
            _print_outer_row_sep()

        for lr in range(3):
            # Numéro de ligne globale (1-9)
            global_row = gr * 3 + lr + 1
            row_str = f"{global_row} "

            for gc in range(3):
                if gc > 0:
                    row_str += ' || '

                # Si la sous-grille est terminée : afficher son résultat centré
                if board.local_winner[gr][gc] != EMPTY:
                    row_str += _render_won_subgrid_row(
                        board.local_winner[gr][gc], lr
                    )
                else:
                    # Afficher les 3 cases de cette ligne dans cette sous-grille
                    for lc in range(3):
                        if lc > 0:
                            row_str += '|'
                        cell = board.cells[gr][gc][lr][lc]
                        sym = _SYM[cell]

                        # Mettre en évidence le dernier coup
                        if last_move and (gr, gc, lr, lc) == last_move:
                            sym = f'[{sym}]'
                        else:
                            sym = f' {sym} '
                        row_str += sym

            print(row_str)

    print()
    _print_col_header()
    _print_status(board)
    print()


def _print_col_header():
    """Affiche l'en-tête des colonnes 1 à 9."""
    header = '  '
    for gc in range(3):
        if gc > 0:
            header += '   '
        for lc in range(3):
            col = gc * 3 + lc + 1
            header += f' {col} '
    print(header)


def _print_outer_row_sep():
    """Affiche un séparateur horizontal entre deux lignes de sous-grilles."""
    sep = '  '
    for gc in range(3):
        if gc > 0:
            sep += '==='
        sep += '==========='
    print(sep)


def _render_won_subgrid_row(winner, lr):
    """
    Pour une sous-grille terminée, retourne la chaîne à afficher
    pour la ligne locale `lr` (0, 1 ou 2).

    La ligne centrale (lr=1) affiche le vainqueur centré.
    """
    sym = _WIN_SYM.get(winner, '?')
    if lr == 1:
        # Ligne centrale : affiche le grand symbole
        return f'  {sym}  {sym}  '
    else:
        return '         '


def _print_status(board):
    """Affiche les informations sur l'état de la partie."""
    if board.global_winner == EMPTY:
        player_sym = _SYM[board.current_player]
        ag = board.active_grid
        if ag is not None:
            zone = f"sous-grille ({ag[0]+1},{ag[1]+1})"
        else:
            zone = "au choix"
        print(f"  Tour du joueur {player_sym} | Zone : {zone} | Coups : {board.move_count}")
    elif board.global_winner == DRAW:
        print(f"  === MATCH NUL === ({board.move_count} coups)")
    else:
        sym = _SYM[board.global_winner]
        print(f"  === VICTOIRE de {sym} === ({board.move_count} coups)")


def display_move_prompt(board):
    """
    Affiche l'invite de saisie pour le joueur humain.
    Retourne la description de la zone autorisée.
    """
    ag = board.active_grid
    if ag is not None:
        gr, gc = ag
        print(f"  Vous devez jouer dans la sous-grille ({gr+1},{gc+1}).")
        print(f"  Entrez : colonne (1-9) puis ligne (1-9)")
    else:
        print(f"  Vous pouvez jouer dans n'importe quelle sous-grille libre.")
        print(f"  Entrez : colonne (1-9) puis ligne (1-9)")


def display_ai_thinking():
    """Affiche un message pendant que l'IA calcule."""
    print("  [IA réfléchit...]")


def display_ai_move(move):
    """Affiche le coup choisi par l'IA."""
    gr, gc, lr, lc = move
    col = gc * 3 + lc + 1
    row = gr * 3 + lr + 1
    print(f"  [IA joue] colonne={col}, ligne={row}")


def parse_human_move(input_str, board):
    """
    Parse la saisie humaine "col ligne" et retourne le coup (gr, gc, lr, lc)
    ou None si la saisie est invalide.

    La saisie attend deux entiers séparés par un espace : colonne puis ligne (1-9).
    """
    from .rules import get_legal_moves

    parts = input_str.strip().split()
    if len(parts) != 2:
        print("  Erreur : entrez deux nombres séparés par un espace (ex: 5 3).")
        return None

    try:
        col = int(parts[0])
        row = int(parts[1])
    except ValueError:
        print("  Erreur : les deux valeurs doivent être des entiers.")
        return None

    if not (1 <= col <= 9 and 1 <= row <= 9):
        print("  Erreur : colonne et ligne doivent être entre 1 et 9.")
        return None

    # Convertir en indices internes (0-based)
    col -= 1
    row -= 1
    gc = col // 3
    lc = col % 3
    gr = row // 3
    lr = row % 3

    move = (gr, gc, lr, lc)
    legal = get_legal_moves(board)

    if move not in legal:
        print(f"  Coup illégal. Vérifiez la zone active et que la case est libre.")
        return None

    return move