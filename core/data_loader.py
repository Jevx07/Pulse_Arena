"""
core/data_loader.py
Cached JSON loader for all game configuration data.
All modules should use this instead of hardcoding stats.
"""
import json
import os

_cache: dict = {}

_BASE = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(filename: str) -> dict:
    if filename not in _cache:
        path = os.path.join(_BASE, filename)
        with open(path, "r", encoding="utf-8") as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


def get_enemy_stats(type_name: str) -> dict:
    """Return the stat dict for the given enemy type name (e.g. 'rusher')."""
    return _load("enemies.json")[type_name]


def get_weapon(name: str) -> dict:
    """Return the stat dict for the given weapon name (e.g. 'rifle')."""
    return _load("weapons.json")[name]


def get_powerup(name: str) -> dict:
    """Return the config dict for the given powerup name (e.g. 'health')."""
    return _load("powerups.json")[name]


def get_all_enemies() -> dict:
    return _load("enemies.json")


def get_all_weapons() -> dict:
    return _load("weapons.json")


def get_all_powerups() -> dict:
    return _load("powerups.json")
