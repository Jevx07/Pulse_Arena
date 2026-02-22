import math
import random

import pygame

from config.settings import ACCENT_COLOR
from entities.damage_number import DamageNumber
from entities.particle import Particle
from entities.powerup import Powerup, PowerupType


class CombatSystem:
    """
    Handles all hitscan combat: ray-casting, crit rolls, damage, kill
    confirmation, combo tracking, score calculation, and powerup drops.

    State owned here:
        combo            -- current kill streak
        combo_timer      -- frames until combo resets (counts down)
        hitmarker_timer  -- frames to show hit crosshair flash
        screen_flash     -- frames for white screen flash on hit

    State that stays in GameManager (weapon / inventory):
        current_ammo, max_ammo, is_reloading, fire_rate, last_shot,
        screen_shake, score, kills
    """

    def __init__(self):
        self.combo = 0
        self.combo_timer = 0
        self.hitmarker_timer = 0
        self.screen_flash = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_shoot(self, game, mouse_pos):
        """
        Full hitscan pipeline called every frame the player holds LMB.
        Reads ammo state from *game* and writes results back to *game*.
        """
        current_time = pygame.time.get_ticks()

        if (
            game.current_ammo > 0
            and not game.is_reloading
            and current_time - game.last_shot >= game.fire_rate
        ):
            player = game.players[0]
            player_center = player.get_center()

            # --- Muzzle flash particles ---
            for _ in range(8):
                game.particles.append(
                    Particle(
                        player_center[0],
                        player_center[1],
                        ACCENT_COLOR,
                        velocity_range=3,
                        gravity=False,
                    )
                )

            game.current_ammo -= 1
            game.last_shot = current_time

            # --- Ray-cast: find closest enemy inside the aim cone ---
            dx = mouse_pos[0] - player_center[0]
            dy = mouse_pos[1] - player_center[1]

            hit_enemy = self._find_hit_enemy(game.enemies, player_center, dx, dy)

            if hit_enemy:
                self._apply_hit(game, player, hit_enemy)

    def update(self, game):
        """Tick per-frame combat timers. Called from GameManager.update()."""
        if self.combo > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        if self.hitmarker_timer > 0:
            self.hitmarker_timer -= 1

        if self.screen_flash > 0:
            self.screen_flash -= 1

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_hit_enemy(self, enemies, player_center, dx, dy):
        """Return the closest enemy within the aim cone, or None."""
        aim_angle = math.atan2(dy, dx)
        hit_enemy = None
        min_distance = float("inf")

        for enemy in enemies:
            enemy_center = enemy.get_center()
            to_x = enemy_center[0] - player_center[0]
            to_y = enemy_center[1] - player_center[1]

            enemy_angle = math.atan2(to_y, to_x)
            angle_diff = abs(aim_angle - enemy_angle)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff

            distance = math.hypot(to_x, to_y)
            if angle_diff < 0.1 and distance < min_distance:
                hit_enemy = enemy
                min_distance = distance

        return hit_enemy

    def _apply_hit(self, game, player, hit_enemy):
        """Resolve damage, kill, combo, score, particles, and feedback."""
        # --- Damage calculation ---
        # Use current weapon's base damage, scaled by player's damage_boost
        base_damage = game.weapon_system.current_weapon.damage
        damage = int(base_damage * player.damage_boost)

        # Use player's crit_chance (can be upgraded)
        is_critical = random.random() < player.crit_chance
        if is_critical:
            damage = int(damage * 2)

        # --- Floating damage number ---
        game.damage_numbers.append(
            DamageNumber(
                hit_enemy.x + hit_enemy.size // 2,
                hit_enemy.y,
                damage,
                is_critical,
            )
        )

        killed = hit_enemy.take_damage(damage)

        if killed:
            self._on_kill(game, player, hit_enemy)
        else:
            self._on_hit(game, hit_enemy)

        # --- Per-shot feedback (always, kill or not) ---
        self.hitmarker_timer = 10
        self.screen_flash = 5

    def _on_kill(self, game, player, enemy):
        """Handle an enemy kill: combo, score, particles, powerup drop."""
        game.kills += 1

        # Combo
        self.combo += 1
        self.combo_timer = 180

        # Score with combo multiplier
        combo_multiplier = 1 + (self.combo * 0.1)
        game.score += int(enemy.score_value * combo_multiplier)

        # Lifesteal (P3 upgrade)
        if player.lifesteal > 0:
            player.health = min(player.max_health, player.health + player.lifesteal)

        # Death burst particles
        cx = enemy.x + enemy.size // 2
        cy = enemy.y + enemy.size // 2
        for _ in range(25):
            game.particles.append(
                Particle(cx, cy, enemy.color, velocity_range=6)
            )

        # Powerup drop (30% chance)
        self._maybe_drop_powerup(game, cx, cy)

        game.enemies.remove(enemy)
        game.screen_shake = 6

    def _on_hit(self, game, enemy):
        """Handle a non-lethal hit: spark particles + light shake."""
        cx = enemy.x + enemy.size // 2
        cy = enemy.y + enemy.size // 2
        for _ in range(5):
            game.particles.append(
                Particle(cx, cy, (255, 255, 100), velocity_range=2, gravity=False)
            )
        game.screen_shake = 2

    def _maybe_drop_powerup(self, game, x, y):
        """30% chance to drop a random powerup at the given position."""
        if random.random() < 0.3:
            powerup_type = random.choice(list(PowerupType))
            game.powerups.append(Powerup(x, y, powerup_type))
