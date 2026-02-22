import math

import pygame

from config.settings import (
    WIDTH,
    HEIGHT,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
)
from entities.powerup import PowerupType


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


class Player:
    def __init__(self, x, y, player_id=0):
        self.id = player_id
        self.x = x
        self.y = y
        self.size = 45
        self.base_speed = 6
        self.speed = self.base_speed
        self.health = 100
        self.max_health = 100
        self.color = SECONDARY_COLOR
        self.invulnerable_time = 0
        self.is_invulnerable = False

        self.damage_boost = 1.0
        self.damage_boost_timer = 0
        self.speed_boost_timer = 0
        self.shield_active = False
        self.shield_timer = 0

        # P3 — Upgrade fields
        self.crit_chance = 0.15
        self.lifesteal = 0           # HP restored on kill
        self.dash_unlocked = False
        self.dash_cooldown = 0

        self.damage_direction = None
        self.damage_indicator_timer = 0

    def update(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

        if self.is_invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.is_invulnerable = False

        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= 1
            if self.damage_boost_timer == 0:
                self.damage_boost = 1.0

        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            self.speed = self.base_speed * 1.5
        else:
            self.speed = self.base_speed

        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False

        if self.damage_indicator_timer > 0:
            self.damage_indicator_timer -= 1

    def take_damage(self, amount, direction=None):
        if self.shield_active:
            self.shield_active = False
            self.shield_timer = 0
            return False

        if not self.is_invulnerable:
            self.health -= amount
            self.is_invulnerable = True
            self.invulnerable_time = 30
            self.damage_direction = direction
            self.damage_indicator_timer = 30
            return True
        return False

    def apply_powerup(self, powerup_type):
        if powerup_type == PowerupType.HEALTH:
            self.health = min(self.max_health, self.health + 30)
        elif powerup_type == PowerupType.DAMAGE_BOOST:
            self.damage_boost = 2.0
            self.damage_boost_timer = 300
        elif powerup_type == PowerupType.SPEED_BOOST:
            self.speed_boost_timer = 300
        elif powerup_type == PowerupType.SHIELD:
            self.shield_active = True
            self.shield_timer = 300

    def draw(self, screen, particles):
        if self.shield_active:
            shield_pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
            pygame.draw.circle(
                screen,
                (200, 100, 255),
                (int(self.x + self.size // 2), int(self.y + self.size // 2)),
                int(self.size // 2 + 15 + shield_pulse),
                2,
            )

        if self.damage_indicator_timer > 0 and self.damage_direction:
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            angle = math.atan2(self.damage_direction[1], self.damage_direction[0])

            indicator_length = 40
            end_x = center_x + math.cos(angle) * indicator_length
            end_y = center_y + math.sin(angle) * indicator_length

            alpha = int(255 * (self.damage_indicator_timer / 30))
            indicator_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(
                indicator_surf,
                (*ACCENT_COLOR, alpha),
                (center_x, center_y),
                (end_x, end_y),
                5,
            )
            screen.blit(indicator_surf, (0, 0))

        if not self.is_invulnerable or (self.invulnerable_time // 5) % 2 == 0:
            glow_color = self.color
            if self.damage_boost > 1.0:
                glow_color = (255, 100, 100)

            glow = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
            pygame.draw.rect(
                glow,
                (*glow_color, 50),
                (0, 0, self.size + 20, self.size + 20),
                border_radius=8,
            )
            screen.blit(glow, (self.x - 10, self.y - 10))

            draw_rounded_rect(
                screen,
                glow_color,
                (self.x, self.y, self.size, self.size),
                radius=6,
            )
            draw_rounded_rect(
                screen,
                TEXT_COLOR,
                (self.x, self.y, self.size, self.size),
                radius=6,
                border=2,
                border_color=TEXT_COLOR,
            )

    def get_center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def is_alive(self):
        return self.health > 0

