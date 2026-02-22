"""
core/stats_tracker.py
Persists player stats to data/profile.json.
commit_run() includes a guard so it fires ONCE per game-over transition
(prevents double-writes on restart loops).
"""
import json
import os


_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "profile.json")

_DEFAULTS = {
    "highest_wave": 0,
    "total_kills": 0,
    "best_score": 0,
    "longest_combo": 0,
    "games_played": 0,
}


class StatsTracker:
    def __init__(self):
        self.profile = self._load()
        self._committed = False   # transition guard: fire once per game-over

    def commit_run(self, game):
        """
        Call ONCE when state transitions to STATE_GAME_OVER.
        Updates personal bests and writes profile.json.
        Guard prevents double-writes on restart loops.
        """
        if self._committed:
            return
        self._committed = True

        p = self.profile
        p["games_played"] += 1
        p["highest_wave"]  = max(p["highest_wave"],  game.wave)
        p["total_kills"]  += game.kills
        p["best_score"]    = max(p["best_score"],    game.score)
        p["longest_combo"] = max(p["longest_combo"], game.combat.combo)

        self._save()

    def reset_guard(self):
        """Reset guard when the game restarts."""
        self._committed = False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if os.path.exists(_PROFILE_PATH):
            try:
                with open(_PROFILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge missing keys from defaults
                    for k, v in _DEFAULTS.items():
                        data.setdefault(k, v)
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return dict(_DEFAULTS)

    def _save(self):
        os.makedirs(os.path.dirname(_PROFILE_PATH), exist_ok=True)
        with open(_PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2)
