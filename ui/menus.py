import math

import pygame

from config.settings import WIDTH, HEIGHT, ACCENT_COLOR, UI_BG, UI_BORDER, TEXT_COLOR, SECONDARY_COLOR
from ui.hud import draw_rounded_rect


def draw_game_over(screen, game):
    font_huge   = pygame.font.Font(None, 96)
    font_large  = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 48)
    font_small  = pygame.font.Font(None, 36)
    font_tiny   = pygame.font.Font(None, 26)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    game_over_text = font_huge.render("GAME OVER", True, ACCENT_COLOR)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(game_over_text, game_over_rect)

    # ── Run stats panel ──────────────────────────────────────────────
    panel_w, panel_h = 480, 240
    panel_x = WIDTH // 2 - panel_w // 2
    panel_y = HEIGHT // 2 - 100

    draw_rounded_rect(screen, UI_BG, (panel_x, panel_y, panel_w, panel_h), radius=15)
    draw_rounded_rect(screen, ACCENT_COLOR,
                      (panel_x, panel_y, panel_w, panel_h),
                      radius=15, border=3, border_color=ACCENT_COLOR)

    y = panel_y + 30
    rows = [
        (f"Wave Reached:   {game.wave}",   TEXT_COLOR),
        (f"Eliminations:   {game.kills}",  SECONDARY_COLOR),
        (f"Score:   {game.score}",          (255, 215, 0)),
    ]
    for text, color in rows:
        surf = font_medium.render(text, True, color)
        screen.blit(surf, (panel_x + 40, y))
        y += 65

    # ── Personal best panel ──────────────────────────────────────────
    pb = game.stats.profile
    pb_w, pb_h = 300, 160
    pb_x = WIDTH // 2 - pb_w // 2
    pb_y = panel_y + panel_h + 20

    draw_rounded_rect(screen, (15, 18, 30), (pb_x, pb_y, pb_w, pb_h), radius=10)
    draw_rounded_rect(screen, UI_BORDER, (pb_x, pb_y, pb_w, pb_h),
                      radius=10, border=1, border_color=UI_BORDER)

    pb_label = font_tiny.render("PERSONAL BESTS", True, UI_BORDER)
    screen.blit(pb_label, pb_label.get_rect(center=(WIDTH // 2, pb_y + 18)))

    bests = [
        ("Best Wave",  pb["highest_wave"]),
        ("Best Score", pb["best_score"]),
        ("Games",      pb["games_played"]),
    ]
    bx = pb_x + 20
    for i, (label, val) in enumerate(bests):
        col_x = bx + i * 90
        val_surf  = font_small.render(str(val),   True, SECONDARY_COLOR)
        lbl_surf  = font_tiny.render(label,        True, UI_BORDER)
        screen.blit(val_surf,  val_surf.get_rect(centerx=col_x + 35, y=pb_y + 45))
        screen.blit(lbl_surf, lbl_surf.get_rect(centerx=col_x + 35, y=pb_y + 80))

    # ── Restart prompt ───────────────────────────────────────────────
    restart_text = font_small.render("Press SPACE to Restart", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 60))

    alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.005))
    restart_surf = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
    restart_surf.fill((255, 255, 255, alpha))
    restart_text.blit(restart_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(restart_text, restart_rect)
