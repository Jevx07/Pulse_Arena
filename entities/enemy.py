import math
import random
from enum import Enum

import pygame

from config.settings import ACCENT_COLOR, WIDTH, HEIGHT
from core.data_loader import get_enemy_stats


class EnemyType(Enum):
    RUSHER = "rusher"
    TANK = "tank"
    SHOOTER = "shooter"
    SWARM = "swarm"
    HUNTER = "hunter"
    SNIPER = "sniper"
    SUPPORT = "support"


class AIState(Enum):
    CHASE = 1
    ATTACK = 2
    RETREAT = 3
    STRAFE = 4
    FLANK = 5       # Hunter: perpendicular approach
    AIM = 6         # Sniper: laser lock-on before firing
    SUPPORT_IDLE = 7  # Support: stationary heal aura


def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


class Enemy:
    def __init__(self, x, y, wave_number, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.wave = wave_number

        # --- Load stats from JSON data config ---
        stats = get_enemy_stats(enemy_type.value)
        self.size = stats["size"]
        self.base_speed = stats["base_speed"]
        self.health = stats["health"]
        self.damage = stats["damage"]
        self.color = tuple(stats["color"])
        self.score_value = stats["score_value"]

        # Wave scaling
        self.speed = self.base_speed + (wave_number * 0.08)
        self.health = int(self.health * (1 + wave_number * 0.1))
        self.max_health = self.health

        # --- AI state ---
        self.state = AIState.CHASE
        self.state_timer = 0
        self.shoot_cooldown = 0
        self.strafe_direction = random.choice([-1, 1])

        # Hunter flank direction (perpendicular side)
        self.flank_side = random.choice([-1, 1])
        self.flank_switch_timer = 0

        # Sniper
        self.aim_timer = 0          # counts up to 60 before firing
        self.sniper_cooldown = 0    # frames between sniper shots
        self.laser_target: tuple | None = None  # (x, y) of player during AIM state

        # Support
        self.heal_tick = 0          # counts up to 60 for heal pulse

        # Hit feedback
        self.hit_flash = 0
        self.slow_timer = 0         # P4: enemy briefly slows on hit

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, player_pos, nearby_enemies=None):
        """
        Update enemy AI.
        Args:
            player_pos: (x, y) tuple of the player's center
            nearby_enemies: list of other Enemy instances (for Support heal)
        Returns:
            (should_shoot, direction) — direction is normalised (dx, dy) or None
        """
        if nearby_enemies is None:
            nearby_enemies = []

        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2

        dx = player_pos[0] - center_x
        dy = player_pos[1] - center_y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.sniper_cooldown > 0:
            self.sniper_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1

        # Effective speed reduced on hit-slow (P4)
        effective_speed = self.speed * (0.7 if self.slow_timer > 0 else 1.0)

        should_shoot = False
        shoot_dir = None

        # ---- Type-specific AI ----
        if self.type == EnemyType.SHOOTER:
            should_shoot, shoot_dir = self._ai_shooter(
                dx, dy, distance, effective_speed
            )
        elif self.type == EnemyType.HUNTER:
            self._ai_hunter(dx, dy, distance, effective_speed, player_pos)
        elif self.type == EnemyType.SNIPER:
            should_shoot, shoot_dir = self._ai_sniper(
                dx, dy, distance, effective_speed, player_pos
            )
        elif self.type == EnemyType.SUPPORT:
            self._ai_support(dx, dy, distance, effective_speed, nearby_enemies)
        else:
            # RUSHER, TANK, SWARM — simple chase
            self.x += dx * effective_speed
            self.y += dy * effective_speed

        # Clamp to screen bounds
        self.x = max(-self.size, min(WIDTH, self.x))
        self.y = max(-self.size, min(HEIGHT, self.y))

        return should_shoot, shoot_dir

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 10
        self.slow_timer = 5   # P4: brief slow on hit
        return self.health <= 0

    def draw(self, screen):
        color = (255, 255, 255) if self.hit_flash > 0 else self.color

        if self.type == EnemyType.TANK:
            draw_rounded_rect(screen, color, (self.x, self.y, self.size, self.size), radius=5)
            draw_rounded_rect(screen, (100, 30, 30), (self.x, self.y, self.size, self.size),
                              radius=5, border=4, border_color=(100, 30, 30))

        elif self.type == EnemyType.SHOOTER:
            points = [
                (self.x + self.size // 2, self.y),
                (self.x, self.y + self.size),
                (self.x + self.size, self.y + self.size),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (150, 50, 150), points, 2)

        elif self.type == EnemyType.HUNTER:
            # Diamond shape — aggressive silhouette
            cx = self.x + self.size // 2
            cy = self.y + self.size // 2
            r = self.size // 2
            points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (180, 30, 30), points, 2)

        elif self.type == EnemyType.SNIPER:
            # Thin elongated rectangle — long-range feel
            draw_rounded_rect(screen, color,
                              (self.x + self.size // 4, self.y, self.size // 2, self.size),
                              radius=3)
            # Draw laser during AIM state
            if self.state == AIState.AIM and self.laser_target:
                cx = self.x + self.size // 2
                cy = self.y + self.size // 2
                alpha = min(255, int(255 * (self.aim_timer / 60)))
                laser_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(laser_surf, (255, 50, 50, alpha),
                                 (cx, cy), self.laser_target, 2)
                # Small dot at muzzle
                pygame.draw.circle(laser_surf, (255, 100, 100, alpha), (cx, cy), 4)
                screen.blit(laser_surf, (0, 0))

        elif self.type == EnemyType.SUPPORT:
            # Hexagonal aura shape
            cx = self.x + self.size // 2
            cy = self.y + self.size // 2
            r = self.size // 2
            hex_pts = [
                (cx + r * math.cos(math.radians(60 * i - 30)),
                 cy + r * math.sin(math.radians(60 * i - 30)))
                for i in range(6)
            ]
            pygame.draw.polygon(screen, color, hex_pts)
            pygame.draw.polygon(screen, (30, 80, 200), hex_pts, 2)
            # Pulsing aura ring
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 15
            aura_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (60, 120, 220, 40),
                               (int(cx), int(cy)), int(120 + pulse), 2)
            screen.blit(aura_surf, (0, 0))

        else:
            # RUSHER, SWARM
            draw_rounded_rect(screen, color, (self.x, self.y, self.size, self.size), radius=5)
            draw_rounded_rect(screen,
                              tuple(max(0, c - 50) for c in self.color),
                              (self.x, self.y, self.size, self.size),
                              radius=5, border=2,
                              border_color=tuple(max(0, c - 50) for c in self.color))

        # Health bar (all types)
        bar_w = self.size
        hp_pct = self.health / self.max_health
        bar_x, bar_y = self.x, self.y - 10
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, 5), border_radius=2)
        if hp_pct > 0:
            bar_color = ACCENT_COLOR if hp_pct < 0.3 else (255, 150, 50)
            pygame.draw.rect(screen, bar_color,
                             (bar_x, bar_y, int(bar_w * hp_pct), 5), border_radius=2)

        # Support: draw role icon above health bar
        if self.type == EnemyType.SUPPORT:
            font = pygame.font.Font(None, 18)
            label = font.render("SUP", True, (100, 180, 255))
            screen.blit(label, (self.x, self.y - 22))

        if self.type == EnemyType.SNIPER and self.state == AIState.AIM:
            font = pygame.font.Font(None, 18)
            label = font.render("AIM", True, (255, 200, 50))
            screen.blit(label, (self.x, self.y - 22))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def is_alive(self):
        return self.health > 0

    # ------------------------------------------------------------------
    # Private AI helpers — NO GameManager reference
    # ------------------------------------------------------------------

    def _ai_shooter(self, dx, dy, distance, speed):
        """Strafe/retreat ranged attacker."""
        if distance > 200:
            self.state = AIState.CHASE
        elif distance < 150:
            self.state = AIState.RETREAT
        else:
            self.state = AIState.STRAFE

        if self.state == AIState.CHASE:
            self.x += dx * speed
            self.y += dy * speed
        elif self.state == AIState.RETREAT:
            self.x -= dx * speed * 0.7
            self.y -= dy * speed * 0.7
        elif self.state == AIState.STRAFE:
            perp_dx, perp_dy = -dy, dx
            self.x += perp_dx * speed * self.strafe_direction
            self.y += perp_dy * speed * self.strafe_direction
            if random.random() < 0.02:
                self.strafe_direction *= -1

        should_shoot = False
        if self.shoot_cooldown == 0 and distance < 400:
            should_shoot = True
            self.shoot_cooldown = 90

        return should_shoot, (dx, dy) if should_shoot else None

    def _ai_hunter(self, dx, dy, distance, speed, player_pos):
        """
        Flanks the player by approaching from a perpendicular angle.
        Lightly predicts player position to create pressure.
        """
        self.state = AIState.FLANK
        self.flank_switch_timer += 1
        if self.flank_switch_timer > 120:
            self.flank_side *= -1
            self.flank_switch_timer = 0

        # Slight movement prediction: aim ahead of where player is
        predict_x = player_pos[0] + dx * 20
        predict_y = player_pos[1] + dy * 20

        cx = self.x + self.size // 2
        cy = self.y + self.size // 2
        pdx = predict_x - cx
        pdy = predict_y - cy
        pdist = math.hypot(pdx, pdy)
        if pdist > 0:
            pdx /= pdist
            pdy /= pdist

        # Perpendicular component
        perp_dx = -pdy * self.flank_side
        perp_dy = pdx * self.flank_side

        # Blend: 60% approach + 40% flank
        move_x = pdx * 0.6 + perp_dx * 0.4
        move_y = pdy * 0.6 + perp_dy * 0.4

        self.x += move_x * speed
        self.y += move_y * speed

    def _ai_sniper(self, dx, dy, distance, speed, player_pos):
        """
        Keeps range, locks on with a laser indicator for 60 frames, then fires.
        """
        should_shoot = False
        shoot_dir = None

        if distance > 350:
            # Move into range
            self.state = AIState.CHASE
            self.x += dx * speed
            self.y += dy * speed
            self.aim_timer = 0
            self.laser_target = None
        elif self.sniper_cooldown > 0:
            # Post-shot recovery — hold position
            self.state = AIState.STRAFE
            perp_dx, perp_dy = -dy, dx
            self.x += perp_dx * speed * 0.5
            self.y += perp_dy * speed * 0.5
            self.laser_target = None
        else:
            # AIM state: stand still, charge up laser
            self.state = AIState.AIM
            self.laser_target = (int(player_pos[0]), int(player_pos[1]))
            self.aim_timer += 1
            if self.aim_timer >= 60:
                should_shoot = True
                shoot_dir = (dx, dy)
                self.sniper_cooldown = 120
                self.aim_timer = 0
                self.laser_target = None

        return should_shoot, shoot_dir

    def _ai_support(self, dx, dy, distance, speed, nearby_enemies):
        """
        Maintains distance from player; heals nearby allies every 60 frames.
        """
        if distance < 250:
            # Slowly retreat
            self.state = AIState.SUPPORT_IDLE
            self.x -= dx * speed * 0.5
            self.y -= dy * speed * 0.5
        else:
            # Drift gently towards player to stay in healing radius
            self.state = AIState.CHASE
            self.x += dx * speed * 0.3
            self.y += dy * speed * 0.3

        # Heal pulse every 60 frames
        self.heal_tick += 1
        if self.heal_tick >= 60:
            self.heal_tick = 0
            cx = self.x + self.size // 2
            cy = self.y + self.size // 2
            for other in nearby_enemies:
                if other is self:
                    continue
                ox = other.x + other.size // 2
                oy = other.y + other.size // 2
                if math.hypot(ox - cx, oy - cy) <= 120:
                    other.health = min(other.max_health, other.health + 2)
