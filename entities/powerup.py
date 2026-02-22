import math
from enum import Enum

import pygame


class PowerupType(Enum):
    HEALTH = 1
    AMMO = 2
    DAMAGE_BOOST = 3
    SPEED_BOOST = 4
    SHIELD = 5


class Powerup:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.size = 25
        self.lifetime = 600
        self.pulse = 0

        self.colors = {
            PowerupType.HEALTH: (100, 255, 100),
            PowerupType.AMMO: (255, 200, 100),
            PowerupType.DAMAGE_BOOST: (255, 100, 100),
            PowerupType.SPEED_BOOST: (100, 200, 255),
            PowerupType.SHIELD: (200, 100, 255),
        }

    def update(self):
        self.lifetime -= 1
        self.pulse += 0.1

    def draw(self, screen):
        scale = 1 + math.sin(self.pulse) * 0.15
        size = int(self.size * scale)
        color = self.colors[self.type]

        glow = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, 50), (size * 1.5, size * 1.5), size * 1.5)
        screen.blit(glow, (self.x - size * 1.5, self.y - size * 1.5))

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size, 3)

        font = pygame.font.Font(None, 20)
        symbols = {
            PowerupType.HEALTH: "+",
            PowerupType.AMMO: "A",
            PowerupType.DAMAGE_BOOST: "D",
            PowerupType.SPEED_BOOST: "S",
            PowerupType.SHIELD: "X",
        }
        text = font.render(symbols[self.type], True, color)
        screen.blit(text, (int(self.x - 6), int(self.y - 8)))

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2,
        )

    def is_expired(self):
        return self.lifetime <= 0

