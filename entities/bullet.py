import pygame

from config.settings import WIDTH, HEIGHT


class EnemyBullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 5
        self.speed = 8
        self.color = (255, 150, 50)

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(
            screen,
            (255, 200, 100),
            (int(self.x), int(self.y)),
            self.radius - 2,
        )

    def is_off_screen(self):
        return (
            self.x < -50
            or self.x > WIDTH + 50
            or self.y < -50
            or self.y > HEIGHT + 50
        )

    def get_pos(self):
        return (self.x, self.y)

