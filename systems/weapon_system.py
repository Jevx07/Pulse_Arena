"""
systems/weapon_system.py

WeaponSystem owns the full firing pipeline.
GameManager calls: game.weapon_system.handle_shoot(player, enemies, mouse_pos, game)
CombatSystem only handles kill resolution, combo, and score.
"""
import math
import random
from dataclasses import dataclass, field

import pygame

from config.settings import ACCENT_COLOR
from core.data_loader import get_weapon
from entities.damage_number import DamageNumber
from entities.particle import Particle


@dataclass
class Weapon:
    key: str
    name: str
    max_ammo: int
    damage: int
    fire_rate: int       # minimum frames between shots
    reload_time: int     # milliseconds
    spread_count: int    # number of rays per shot (shotgun = 5)
    spread_angle: float  # total spread in radians (shotgun only)
    charge_frames: int   # frames to hold before firing (railgun)
    burst_count: int     # shots per trigger pull (burst = 3)
    burst_interval: int  # frames between burst shots

    @staticmethod
    def from_json(key: str) -> "Weapon":
        d = get_weapon(key)
        return Weapon(
            key=key,
            name=d["name"],
            max_ammo=d["max_ammo"],
            damage=d["damage"],
            fire_rate=d["fire_rate"],
            reload_time=d["reload_time"],
            spread_count=d["spread_count"],
            spread_angle=d.get("spread_angle", 0.0),
            charge_frames=d["charge_frames"],
            burst_count=d["burst_count"],
            burst_interval=d["burst_interval"],
        )


# ─── Presets ──────────────────────────────────────────────────────────────────
RIFLE       = Weapon.from_json("rifle")
SMG         = Weapon.from_json("smg")
SHOTGUN     = Weapon.from_json("shotgun")
RAILGUN     = Weapon.from_json("railgun")
BURST_RIFLE = Weapon.from_json("burst_rifle")

ALL_WEAPONS = [RIFLE, SMG, SHOTGUN, RAILGUN, BURST_RIFLE]


class WeaponSystem:
    """
    Owns firing logic for all weapon types.
    Reads ammo state from the game object and writes results back.
    """

    def __init__(self, weapon: Weapon = None):
        self.current_weapon: Weapon = weapon or RIFLE

        # Shared state
        self.charge_held: int = 0       # railgun charge counter
        self.burst_queue: int = 0       # remaining burst shots
        self.burst_tick: int = 0        # countdown until next burst shot
        self.last_shot: int = 0         # pygame ticks of last fired shot

        # P4 feedback
        self.crosshair_spread: int = 0  # pixels added to crosshair gap, decays

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def equip(self, weapon: Weapon, game):
        """Swap to a new weapon and reset ammo in GameManager."""
        self.current_weapon = weapon
        self.charge_held = 0
        self.burst_queue = 0
        self.burst_tick = 0
        game.current_ammo = weapon.max_ammo
        game.max_ammo = weapon.max_ammo
        game.reload_time = weapon.reload_time
        game.is_reloading = False

    def update(self, game):
        """Per-frame tick — handles burst queue and feedback decay."""
        # Burst shot drip-feed
        if self.burst_queue > 0:
            self.burst_tick -= 1
            if self.burst_tick <= 0 and game.current_ammo > 0 and not game.is_reloading:
                self.burst_queue -= 1
                self.burst_tick = self.current_weapon.burst_interval
                self._fire_single(game, game._last_mouse_pos)

        # Crosshair spread decay (P4)
        if self.crosshair_spread > 0:
            self.crosshair_spread -= 1

    def handle_shoot(self, game, mouse_pos, mouse_held: bool):
        """
        Called every frame the player holds/clicks LMB.
        mouse_held=True means button is being held (continuous fire).
        """
        # Store mouse pos so burst update can access it
        game._last_mouse_pos = mouse_pos

        w = self.current_weapon
        current_time = pygame.time.get_ticks()

        if game.is_reloading or game.current_ammo <= 0:
            return

        # Railgun — charge while held, fire on release
        if w.charge_frames > 0:
            if mouse_held:
                self.charge_held = min(w.charge_frames, self.charge_held + 1)
            else:
                if self.charge_held >= w.charge_frames:
                    self._fire_railgun(game, mouse_pos)
                self.charge_held = 0
            return

        # Fire rate check
        if current_time - self.last_shot < w.fire_rate * (1000 // 60):
            return

        # Burst rifle — queue burst on trigger pull (edge-detect via last_shot gap)
        if w.burst_count > 1:
            if self.burst_queue == 0:
                self.burst_queue = w.burst_count - 1  # first shot fires now
                self.burst_tick = w.burst_interval
                self._fire_single(game, mouse_pos)
            return

        # Shotgun — multi-ray spread
        if w.spread_count > 1:
            self._fire_shotgun(game, mouse_pos)
            return

        # Default: single shot
        self._fire_single(game, mouse_pos)

    # ------------------------------------------------------------------
    # Charge bar (used by HUD)
    # ------------------------------------------------------------------

    def get_charge_pct(self) -> float:
        """Returns 0.0–1.0 charge progress for the railgun."""
        if self.current_weapon.charge_frames == 0:
            return 0.0
        return self.charge_held / self.current_weapon.charge_frames

    # ------------------------------------------------------------------
    # Private firing methods
    # ------------------------------------------------------------------

    def _fire_single(self, game, mouse_pos):
        """Fire one ray in the cursor direction."""
        player = game.players[0]
        player_center = player.get_center()
        self._muzzle_flash(game, player_center)
        game.current_ammo -= 1
        self.last_shot = pygame.time.get_ticks()
        self.crosshair_spread = 8   # P4

        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        hit_enemy = self._raycast(game.enemies, player_center, dx, dy)
        if hit_enemy:
            game.combat._apply_hit(game, player, hit_enemy)

    def _fire_shotgun(self, game, mouse_pos):
        """Fire spread_count rays in a cone."""
        player = game.players[0]
        player_center = player.get_center()
        self._muzzle_flash(game, player_center, count=12)
        game.current_ammo -= 1
        self.last_shot = pygame.time.get_ticks()
        self.crosshair_spread = 14  # P4 — wider spread for shotgun

        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        base_angle = math.atan2(dy, dx)
        w = self.current_weapon
        half = w.spread_angle / 2

        hits = set()
        for i in range(w.spread_count):
            angle_offset = -half + (w.spread_angle / (w.spread_count - 1)) * i
            ray_angle = base_angle + angle_offset
            rdx = math.cos(ray_angle)
            rdy = math.sin(ray_angle)
            hit = self._raycast(game.enemies, player_center, rdx, rdy)
            if hit and hit not in hits:
                hits.add(hit)
                game.combat._apply_hit(game, player, hit)

    def _fire_railgun(self, game, mouse_pos):
        """Fully-charged railgun shot — pierces first enemy, massive damage."""
        player = game.players[0]
        player_center = player.get_center()
        # Dramatic muzzle flash
        for _ in range(20):
            game.particles.append(
                Particle(player_center[0], player_center[1],
                         (120, 200, 255), velocity_range=5, gravity=False)
            )
        game.current_ammo -= 1
        self.last_shot = pygame.time.get_ticks()
        self.crosshair_spread = 0   # Railgun is precise

        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        hit_enemy = self._raycast(game.enemies, player_center, dx, dy, cone=0.05)
        if hit_enemy:
            game.combat._apply_hit(game, player, hit_enemy)

    # ------------------------------------------------------------------
    # Ray-cast helper
    # ------------------------------------------------------------------

    @staticmethod
    def _raycast(enemies, origin, dx, dy, cone=0.1):
        """
        Return the closest enemy within the aim cone, or None.
        cone: half-angle tolerance in radians.
        """
        aim_angle = math.atan2(dy, dx)
        hit_enemy = None
        min_distance = float("inf")

        for enemy in enemies:
            ex, ey = enemy.get_center()
            to_x = ex - origin[0]
            to_y = ey - origin[1]
            enemy_angle = math.atan2(to_y, to_x)
            angle_diff = abs(aim_angle - enemy_angle)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            dist = math.hypot(to_x, to_y)
            if angle_diff < cone and dist < min_distance:
                hit_enemy = enemy
                min_distance = dist

        return hit_enemy

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    @staticmethod
    def _muzzle_flash(game, pos, count=8):
        for _ in range(count):
            game.particles.append(
                Particle(pos[0], pos[1], ACCENT_COLOR, velocity_range=3, gravity=False)
            )
