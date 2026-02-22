"""
systems/upgrade_system.py
Mid-match upgrade pool and selection logic.
Called after each wave completes. Presents 3 random upgrades to the player.
"""
import random


# Each upgrade: {name, description, apply_fn(player, game)}
UPGRADE_POOL = [
    {
        "name": "Damage Surge",
        "description": "+15% damage permanently",
        "apply_fn": lambda player, game: setattr(
            player, "damage_boost", round(player.damage_boost * 1.15, 3)
        ),
    },
    {
        "name": "Speed Loader",
        "description": "25% faster reload",
        "apply_fn": lambda player, game: setattr(
            game, "reload_time", int(game.reload_time * 0.75)
        ),
    },
    {
        "name": "Lifesteal",
        "description": "+5 HP on every kill",
        "apply_fn": lambda player, game: setattr(
            player, "lifesteal", player.lifesteal + 5
        ),
    },
    {
        "name": "Dash",
        "description": "Shift to dash (120f cooldown)",
        "apply_fn": lambda player, game: setattr(player, "dash_unlocked", True),
    },
    {
        "name": "Crit Focus",
        "description": "+10% critical chance",
        "apply_fn": lambda player, game: setattr(
            player, "crit_chance", round(player.crit_chance + 0.10, 2)
        ),
    },
    {
        "name": "Iron Skin",
        "description": "+20 max HP, fully heal",
        "apply_fn": lambda player, game: (
            setattr(player, "max_health", player.max_health + 20),
            setattr(player, "health", player.max_health),
        ),
    },
    {
        "name": "Rapid Fire",
        "description": "+10% fire rate",
        "apply_fn": lambda player, game: setattr(
            game.weapon_system.current_weapon, "fire_rate",
            max(1, int(game.weapon_system.current_weapon.fire_rate * 0.9)),
        ),
    },
]


def roll_upgrades(n: int = 3) -> list[dict]:
    """Return n non-repeating random upgrades from the pool."""
    return random.sample(UPGRADE_POOL, min(n, len(UPGRADE_POOL)))


def apply_upgrade(upgrade: dict, player, game):
    """Apply the upgrade and emit the event."""
    upgrade["apply_fn"](player, game)
    game.event_bus.emit("EVENT_UPGRADE_APPLIED", name=upgrade["name"])
