import math

import pygame

from config.settings import (
    WIDTH,
    HEIGHT,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    UI_BG,
    UI_BORDER,
    TEXT_COLOR,
)


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


def draw_ui(screen, game):
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
    font_tiny = pygame.font.Font(None, 24)

    player = game.players[0]

    bar_height = 60
    draw_rounded_rect(screen, UI_BG, (40, 20, 400, bar_height), radius=10)
    draw_rounded_rect(
        screen,
        ACCENT_COLOR,
        (40, 20, 400, bar_height),
        radius=10,
        border=2,
        border_color=ACCENT_COLOR,
    )

    title = font_medium.render("PULSE ARENA", True, TEXT_COLOR)
    screen.blit(title, (60, 32))
    pygame.draw.line(screen, SECONDARY_COLOR, (50, 55), (200, 55), 3)

    wave_text = font_small.render(f"WAVE {game.wave}", True, ACCENT_COLOR)
    screen.blit(wave_text, (WIDTH // 2 - 60, 35))

    bar_width = 300
    bar_height = 30
    x = 50
    y = HEIGHT - 80

    draw_rounded_rect(screen, UI_BG, (x - 5, y - 5, bar_width + 10, bar_height + 10), radius=8)
    draw_rounded_rect(
        screen,
        UI_BORDER,
        (x - 5, y - 5, bar_width + 10, bar_height + 10),
        radius=8,
        border=2,
        border_color=UI_BORDER,
    )

    health_width = int((player.health / player.max_health) * bar_width)
    if player.health > 60:
        health_color = SECONDARY_COLOR
    elif player.health > 30:
        health_color = (255, 200, 50)
    else:
        health_color = ACCENT_COLOR

    if health_width > 0:
        draw_rounded_rect(screen, health_color, (x, y, health_width, bar_height), radius=6)

    health_text = font_small.render(f"{player.health}", True, TEXT_COLOR)
    screen.blit(health_text, (x + bar_width + 20, y))

    hp_label = font_tiny.render("HP", True, UI_BORDER)
    screen.blit(hp_label, (x + 5, y + 5))

    powerup_y = y - 40
    if player.damage_boost > 1.0:
        boost_text = font_tiny.render(f"DMG x{player.damage_boost}", True, (255, 100, 100))
        screen.blit(boost_text, (x, powerup_y))
    if player.speed_boost_timer > 0:
        speed_text = font_tiny.render("SPEED+", True, (100, 200, 255))
        screen.blit(speed_text, (x + 120, powerup_y))
    if player.shield_active:
        shield_text = font_tiny.render("SHIELD", True, (200, 100, 255))
        screen.blit(shield_text, (x + 220, powerup_y))

    x = WIDTH - 250
    y = HEIGHT - 120

    draw_rounded_rect(screen, UI_BG, (x - 10, y - 10, 220, 90), radius=10)
    draw_rounded_rect(
        screen,
        UI_BORDER,
        (x - 10, y - 10, 220, 90),
        radius=10,
        border=2,
        border_color=UI_BORDER,
    )

    ammo_color = ACCENT_COLOR if game.current_ammo < 5 else TEXT_COLOR
    ammo_text = font_large.render(f"{game.current_ammo}", True, ammo_color)
    screen.blit(ammo_text, (x, y))

    max_text = font_small.render(f"/{game.max_ammo}", True, UI_BORDER)
    screen.blit(max_text, (x + 80, y + 30))

    # Weapon name
    weapon_name = game.weapon_system.current_weapon.name
    weapon_label = font_tiny.render(weapon_name.upper(), True, SECONDARY_COLOR)
    screen.blit(weapon_label, (x, y - 22))

    # Railgun charge bar
    charge_pct = game.weapon_system.get_charge_pct()
    if charge_pct > 0:
        charge_bar_w = 180
        charge_bar_h = 8
        charge_x, charge_y = x, y + 70
        pygame.draw.rect(screen, UI_BORDER,
                         (charge_x, charge_y, charge_bar_w, charge_bar_h),
                         border_radius=4)
        fill = int(charge_bar_w * charge_pct)
        charge_color = (120, 200, 255) if charge_pct < 1.0 else (200, 255, 100)
        pygame.draw.rect(screen, charge_color,
                         (charge_x, charge_y, fill, charge_bar_h),
                         border_radius=4)
        charge_label = font_tiny.render("CHARGE", True, (120, 200, 255))
        screen.blit(charge_label, (charge_x + 50, charge_y - 18))

    if game.is_reloading:
        current_time = pygame.time.get_ticks()
        reload_progress = min(1.0, (current_time - game.last_reload) / game.reload_time)

        reload_bar_width = 180
        reload_bar_height = 8
        reload_x = x
        reload_y = y + 70

        pygame.draw.rect(
            screen,
            UI_BORDER,
            (reload_x, reload_y, reload_bar_width, reload_bar_height),
            border_radius=4,
        )
        progress_width = int(reload_bar_width * reload_progress)
        pygame.draw.rect(
            screen,
            SECONDARY_COLOR,
            (reload_x, reload_y, progress_width, reload_bar_height),
            border_radius=4,
        )

        reload_text = font_tiny.render("RELOADING", True, SECONDARY_COLOR)
        screen.blit(reload_text, (reload_x + 50, reload_y - 20))

    x = WIDTH - 250
    y = 30

    draw_rounded_rect(screen, UI_BG, (x - 10, y - 10, 220, 150), radius=10)
    draw_rounded_rect(
        screen,
        UI_BORDER,
        (x - 10, y - 10, 220, 150),
        radius=10,
        border=2,
        border_color=UI_BORDER,
    )

    score_label = font_tiny.render("SCORE", True, UI_BORDER)
    screen.blit(score_label, (x, y))

    score_text = font_medium.render(f"{game.score}", True, SECONDARY_COLOR)
    screen.blit(score_text, (x, y + 20))

    kills_label = font_tiny.render("ELIMINATIONS", True, UI_BORDER)
    screen.blit(kills_label, (x, y + 70))

    kills_text = font_small.render(f"{game.kills}", True, TEXT_COLOR)
    screen.blit(kills_text, (x, y + 85))

    if game.combat.combo > 1:
        combo_text = font_medium.render(f"x{game.combat.combo} COMBO!", True, (255, 215, 0))
        combo_rect = combo_text.get_rect(center=(WIDTH // 2, 120))

        scale = 1 + (math.sin(pygame.time.get_ticks() * 0.01) * 0.1)
        scaled_combo = pygame.transform.scale(
            combo_text,
            (int(combo_rect.width * scale), int(combo_rect.height * scale)),
        )
        screen.blit(scaled_combo, scaled_combo.get_rect(center=(WIDTH // 2, 120)))

    enemy_count_text = font_tiny.render(f"Enemies: {len(game.enemies)}", True, UI_BORDER)
    screen.blit(enemy_count_text, (50, 100))

    controls_text = font_tiny.render(
        "WASD: Move | LMB: Shoot (Hitscan) | R: Reload",
        True,
        UI_BORDER,
    )
    screen.blit(controls_text, (50, HEIGHT - 30))

