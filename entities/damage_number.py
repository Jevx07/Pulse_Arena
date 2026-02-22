import pygame


class DamageNumber:
    def __init__(self, x, y, damage, is_critical=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.life = 60
        self.is_critical = is_critical
        self.vy = -2

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self, screen):
        font = pygame.font.Font(None, 36 if self.is_critical else 28)
        color = (255, 100, 100) if self.is_critical else (255, 200, 100)
        alpha = int(255 * (self.life / 60))

        text = font.render(f"-{self.damage}", True, color)
        text.set_alpha(alpha)
        screen.blit(text, (int(self.x), int(self.y)))

    def is_dead(self):
        return self.life <= 0

