import pygame

from config.settings import ACCENT_COLOR


def draw_crosshair(screen, mouse_pos, hitmarker_active=False, spread=0):
    mouse_x, mouse_y = mouse_pos
    crosshair_size = 15
    crosshair_gap = 8 + spread
    thickness = 3

    color = (100, 255, 100) if hitmarker_active else ACCENT_COLOR

    pygame.draw.line(
        screen,
        color,
        (mouse_x, mouse_y - crosshair_gap - crosshair_size),
        (mouse_x, mouse_y - crosshair_gap),
        thickness,
    )
    pygame.draw.line(
        screen,
        color,
        (mouse_x, mouse_y + crosshair_gap),
        (mouse_x, mouse_y + crosshair_gap + crosshair_size),
        thickness,
    )
    pygame.draw.line(
        screen,
        color,
        (mouse_x - crosshair_gap - crosshair_size, mouse_y),
        (mouse_x - crosshair_gap, mouse_y),
        thickness,
    )
    pygame.draw.line(
        screen,
        color,
        (mouse_x + crosshair_gap, mouse_y),
        (mouse_x + crosshair_gap + crosshair_size, mouse_y),
        thickness,
    )

    if hitmarker_active:
        marker_size = 10
        pygame.draw.line(
            screen,
            (100, 255, 100),
            (mouse_x - marker_size, mouse_y - marker_size),
            (mouse_x + marker_size, mouse_y + marker_size),
            2,
        )
        pygame.draw.line(
            screen,
            (100, 255, 100),
            (mouse_x + marker_size, mouse_y - marker_size),
            (mouse_x - marker_size, mouse_y + marker_size),
            2,
        )

    pygame.draw.circle(screen, color, (mouse_x, mouse_y), 2)

