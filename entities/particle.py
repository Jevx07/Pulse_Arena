import random

import pygame


class Particle:
    def __init__(self, x, y, color, velocity_range=3, gravity=True):
        self.x = x
        self.y = y
        self.vx = random.uniform(-velocity_range, velocity_range)
        self.vy = random.uniform(-velocity_range, velocity_range)
        self.life = 30
        self.max_life = 30
        self.color = color
        self.size = random.randint(2, 5)
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.gravity:
            self.vy += 0.2

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

    def is_dead(self):
        return self.life <= 0

