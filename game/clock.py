"""clock.py — Gestionnaire d'horloges par joueur et chronométrage global.

Fournit :
- `SimpleClock` : horloge individuelle (start/stop/resume)
- `GameTimer` : deux horloges (X et O) + chronométrage total et helpers

Usage :
    gt = GameTimer()
    gt.start_for(PLAYER_X)
    ... gt.switch_to(PLAYER_O) ...
    gt.stop_all(); gt.get_player_time(PLAYER_X)
"""
from time import perf_counter
from .board import PLAYER_X, PLAYER_O


class SimpleClock:
    def __init__(self):
        self._elapsed = 0.0
        self._running = False
        self._start = 0.0

    def start(self):
        if not self._running:
            self._start = perf_counter()
            self._running = True

    def stop(self):
        if self._running:
            now = perf_counter()
            self._elapsed += now - self._start
            self._running = False

    def reset(self):
        self._elapsed = 0.0
        self._running = False
        self._start = 0.0

    def elapsed(self):
        if self._running:
            return self._elapsed + (perf_counter() - self._start)
        return self._elapsed


class GameTimer:
    def __init__(self):
        self.clock_x = SimpleClock()
        self.clock_o = SimpleClock()
        self._total_start = None
        self._total_end = None
        self._current = None  # PLAYER_X or PLAYER_O

    def start_total(self):
        if self._total_start is None:
            self._total_start = perf_counter()

    def stop_total(self):
        if self._total_end is None:
            self._total_end = perf_counter()

    def start_for(self, player):
        """Démarre (ou reprend) l'horloge du joueur `player`.

        Ne démarre pas la total_time automatiquement (call start_total()).
        """
        self.start_total()
        if player == PLAYER_X:
            self.clock_x.start()
        else:
            self.clock_o.start()
        self._current = player

    def stop_for(self, player):
        if player == PLAYER_X:
            self.clock_x.stop()
        else:
            self.clock_o.stop()
        if self._current == player:
            self._current = None

    def switch_to(self, player):
        """Stoppe l'horloge en cours (si nécessaire) et démarre celle de `player`."""
        # Stop other
        if player == PLAYER_X:
            self.clock_o.stop()
            self.clock_x.start()
        else:
            self.clock_x.stop()
            self.clock_o.start()
        self._current = player

    def stop_all(self):
        self.clock_x.stop()
        self.clock_o.stop()
        self.stop_total()

    def get_player_time(self, player):
        return self.clock_x.elapsed() if player == PLAYER_X else self.clock_o.elapsed()

    def total_time(self):
        if self._total_start is None:
            return 0.0
        end = self._total_end if self._total_end is not None else perf_counter()
        return end - self._total_start
