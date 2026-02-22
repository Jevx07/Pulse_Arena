"""
core/modes/survival_mode.py
Classic survival mode: waves of escalating enemies, boss every 5 waves.
Delegates wave spawning to systems/wave_manager.py.
"""
from config.settings import STATE_PLAYING
from core.modes.base_mode import GameMode
from systems.wave_manager import handle_spawning


class SurvivalMode(GameMode):
    """
    Standard endless-wave survival.
    Owns wave progression logic through handle_spawning().
    Future modes can override on_wave_end() to present different pacing.
    """

    def update(self, game):
        """Per-frame update: tick wave spawning."""
        if game.state == STATE_PLAYING:
            handle_spawning(game)

    def on_enemy_killed(self, game, enemy):
        """Nothing extra for survival — kill counting is done in CombatSystem."""
        pass

    def on_wave_end(self, game):
        """Wave ends naturally via handle_spawning → next_wave()."""
        pass

    def on_player_damaged(self, game, amount):
        """No special survival rule on player damage."""
        pass
