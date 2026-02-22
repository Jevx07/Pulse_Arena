"""
core/modes/base_mode.py
Abstract base class for all game modes.
Future modes (endurance, co-op, pvp) plug in by subclassing GameMode.
"""


class GameMode:
    """
    Interface contract for all game modes.
    All methods receive the full game object so they can read/write any state.
    """

    def update(self, game):
        """Called every frame while state == STATE_PLAYING."""
        ...

    def on_enemy_killed(self, game, enemy):
        """Called immediately after an enemy is confirmed killed."""
        ...

    def on_wave_end(self, game):
        """Called when the last enemy of a wave dies and the wave ends."""
        ...

    def on_player_damaged(self, game, amount):
        """Called whenever the player takes damage."""
        ...
