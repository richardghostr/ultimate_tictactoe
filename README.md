# Ultimate Tic-Tac-Toe — IA Minimax + Alpha-Beta

Ce dépôt contient une implémentation en Python de l'Ultimate Tic-Tac-Toe
(9×9, organisé en 3×3 de sous‑grilles 3×3) avec une IA basée sur
Minimax et élagage Alpha‑Beta. Le code propose une interface texte, une
implémentation complète des règles, une heuristique d'évaluation et des
outils pour faire s'affronter des IA.

Principaux objectifs
- Implémenter un moteur de règles robuste pour l'Ultimate Tic‑Tac‑Toe.
- Développer une IA décisionnelle (Minimax + Alpha‑Beta) avec heuristique.
- Fournir une interface texte simple pour jouer (humain vs IA / IA vs IA).
- Permettre de mesurer et comparer les IA (matchs IA vs IA, scoring DVO).

Fonctionnalités
- Représentation complète du plateau 9×9, copies profondes pour Minimax.
- Génération de coups légaux et application immuable des coups.
- Affichage texte du plateau 9×9 et parsing de la saisie humaine (col, ligne 1–9).
- IA Minimax récursive avec ordering de coups, élagage α/β et approfondissement itératif (timed).
- Heuristique prenant en compte : sous‑grilles gagnées, alignements potentiels,
	valeurs positionnelles (centre/coin/bord) et contrainte de la grille active.
- Suite de tests unitaires couvrant règles, heuristique et comportement de l'IA.

Installation et prérequis
- Python 3.8+ (testé sur 3.10+)
- Aucune dépendance externe requise — juste l'interpréteur Python.

Exemples d'utilisation

Lancer le menu interactif :

```bash
python main.py
```

Mode direct (IA vs IA, profondeur personnalisée) :

```bash
python main.py --mode ai_vs_ai --depth1 4 --depth2 3
```

Mode humain contre IA :

```bash
python main.py --mode human_vs_ai --depth1 4
```

Options utiles
- `--no-display` : désactive l'affichage (utile pour courses de bench IA vs IA).
- `--time-limit <s>` : limite par coup pour l'IA (utilise l'approfondissement itératif).

Tests

Exécuter les tests unitaires :

```bash
python -m pytest -q
```

Structure du projet
- `main.py` — point d'entrée et CLI/menu interactif.
- `game/board.py` — représentation du plateau, copie profonde, état global.
- `game/rules.py` — génération de coups légaux, application de coups, détection des victoires locales et globales.
- `game/display.py` — affichage texte, parsing de la saisie humaine et helpers d'affichage.
- `game/game.py` — boucle de jeu, alternance joueurs, statistiques.
- `ai/minimax.py` — implémentation Minimax + Alpha‑Beta, ordering, iterative deepening timed.
- `ai/heuristic.py` — fonction d'évaluation et constantes de score.
- `ai/player.py` — `HumanPlayer`, `AIPlayer` et factory `make_player`.
- `tests/` — tests unitaires et diagrammes/support (ex: `ultimate_ttt_project_roadmap.svg`).

Design et décisions importantes
- Le plateau est représenté comme une structure 3×3 de sous‑grilles 3×3 pour
	simplifier la logique des victoires locales et de la contrainte "active grid".
- `apply_move` opère sur une copie du `Board` pour que Minimax puisse explorer
	sans effets de bord.
- L'heuristique est conçue pour être informative à profondeur limitée —
	elle combine score de sous‑grilles, alignements potentiels et valeurs positionnelles.
- L'élagage Alpha‑Beta est combiné avec un ordering simple (centre > coins > bords)
	pour améliorer les coupures.

Scoring des confrontations (DVO)
- Victoire rapide : 4 pts
- Victoire lente : 3 pts
- Match nul rapide : 1 pt
- Match nul lent / Défaite : 0 pt

Roadmap (suggérée)
1. Tests & robustesse — coverage et cas limites.
2. Optimisation performance — profiling des appels Minimax, ordering amélioré.
3. Amélioration heuristique — features additionnelles, tuning des poids.
4. Interface légère (optionnel) — web UI ou interface curses.

Contribuer
- Ouvrez une issue pour discuter d'améliorations ou bugs.
- Forkez, créez une branche et proposez un pull request avec tests.

Contact
- Auteur / Mainteneur : vous (projet local). Ajoutez vos coordonnées si besoin.

License
- Aucun header de licence inclus — ajoutez un `LICENSE` si vous souhaitez
	partager publiquement sous une licence précise.
