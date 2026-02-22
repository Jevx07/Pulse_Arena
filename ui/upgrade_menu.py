"""
ui/upgrade_menu.py
Full-screen upgrade card selection screen.
Shows 3 cards with [1] [2] [3] keyboard hints.
State: game must be in STATE_UPGRADE when this is rendered.
"""
import pygame

from config.settings import (
    WIDTH, HEIGHT,
    UI_BG, UI_BORDER, TEXT_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
)


CARD_W = 280
CARD_H = 210
CARD_GAP = 30
CARD_RADIUS = 16


def draw_rounded_rect(surface, color, rect, radius=8, border=0, border_color=None):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
    for cx, cy in [(x + radius, y + radius), (x + w - radius, y + radius),
                   (x + radius, y + h - radius), (x + w - radius, y + h - radius)]:
        pygame.draw.circle(surface, color, (cx, cy), radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_upgrade_menu(screen, upgrades: list[dict], hovered: int = -1):
    """
    Render the upgrade selection overlay.
    upgrades: list of 3 upgrade dicts from upgrade_system.UPGRADE_POOL
    hovered:  index of currently highlighted card (-1 = none)
    """
    # Dark translucent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 210))
    screen.blit(overlay, (0, 0))

    font_title  = pygame.font.Font(None, 52)
    font_header = pygame.font.Font(None, 36)
    font_body   = pygame.font.Font(None, 24)
    font_hint   = pygame.font.Font(None, 28)

    # Title
    title = font_title.render("WAVE COMPLETE — CHOOSE AN UPGRADE", True, SECONDARY_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4 - 50)))

    sub = font_body.render("Press [1], [2], or [3] to select", True, UI_BORDER)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 4 - 15)))

    total_w = CARD_W * 3 + CARD_GAP * 2
    start_x = (WIDTH - total_w) // 2
    card_y = HEIGHT // 4 + 10

    for i, upgrade in enumerate(upgrades):
        cx = start_x + i * (CARD_W + CARD_GAP)

        # Card border glow on hover
        is_hovered = (i == hovered)
        border_color = SECONDARY_COLOR if is_hovered else UI_BORDER
        bg_color = (28, 32, 48) if not is_hovered else (35, 40, 65)

        draw_rounded_rect(screen, bg_color,
                          (cx, card_y, CARD_W, CARD_H), radius=CARD_RADIUS)
        draw_rounded_rect(screen, bg_color,
                          (cx, card_y, CARD_W, CARD_H), radius=CARD_RADIUS,
                          border=2, border_color=border_color)

        # Keyboard hint badge
        hint_surf = font_hint.render(f"[{i+1}]", True, ACCENT_COLOR)
        screen.blit(hint_surf, (cx + 12, card_y + 12))

        # Upgrade name
        name_surf = font_header.render(upgrade["name"], True, TEXT_COLOR)
        screen.blit(name_surf, name_surf.get_rect(
            center=(cx + CARD_W // 2, card_y + 90)))

        # Divider
        pygame.draw.line(screen, UI_BORDER,
                         (cx + 20, card_y + 115), (cx + CARD_W - 20, card_y + 115), 1)

        # Description
        desc_surf = font_body.render(upgrade["description"], True, UI_BORDER)
        screen.blit(desc_surf, desc_surf.get_rect(
            center=(cx + CARD_W // 2, card_y + 145)))

        # Glow dot indicator when hovered
        if is_hovered:
            pygame.draw.circle(screen, SECONDARY_COLOR,
                               (cx + CARD_W // 2, card_y + CARD_H - 15), 5)
