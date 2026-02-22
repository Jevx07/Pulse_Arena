import pygame
import sys
import random

from config.settings import WIDTH, HEIGHT, FPS, BG_COLOR, STATE_PLAYING, STATE_GAME_OVER, STATE_UPGRADE
from core.game_manager import GameManager
from systems.upgrade_system import apply_upgrade
from ui.crosshair import draw_crosshair
from ui.hud import draw_ui
from ui.menus import draw_game_over
from ui.upgrade_menu import draw_upgrade_menu

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pulse Arena")
clock = pygame.time.Clock()


game = GameManager()
pygame.mouse.set_visible(False)

running = True
mouse_held = False

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_held = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False
                # Railgun fires on mouse release
                if game.state == STATE_PLAYING:
                    game.weapon_system.handle_shoot(game, pygame.mouse.get_pos(), mouse_held=False)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game.state == STATE_PLAYING:
                game.reload()

            if event.key == pygame.K_SPACE and game.state == STATE_GAME_OVER:
                game.restart()

            # Upgrade selection: [1] [2] [3]
            if game.state == STATE_UPGRADE and game.pending_upgrades:
                chosen = None
                if event.key == pygame.K_1:
                    chosen = 0
                elif event.key == pygame.K_2:
                    chosen = 1
                elif event.key == pygame.K_3:
                    chosen = 2
                if chosen is not None and chosen < len(game.pending_upgrades):
                    apply_upgrade(game.pending_upgrades[chosen], game.players[0], game)
                    game.pending_upgrades = []
                    game.state = STATE_PLAYING

    # Continuous shooting while mouse held
    if mouse_held and game.state == STATE_PLAYING:
        game.weapon_system.handle_shoot(game, pygame.mouse.get_pos(), mouse_held=True)

    # Update (skips when state != STATE_PLAYING)
    game.update()

    # Draw
    screen.fill(BG_COLOR)

    # Screen flash effect
    if game.combat.screen_flash > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(30 * (game.combat.screen_flash / 5))
        flash_surf.fill((255, 255, 255, alpha))
        screen.blit(flash_surf, (0, 0))

    # Grid background
    grid_spacing = 50
    grid_color = (25, 30, 40)
    for x in range(0, WIDTH, grid_spacing):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, grid_spacing):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)

    # Screen shake offset
    shake_offset = (0, 0)
    if game.screen_shake > 0:
        shake_offset = (random.randint(-game.screen_shake, game.screen_shake),
                       random.randint(-game.screen_shake, game.screen_shake))
        screen.scroll(*shake_offset)

    # Draw game objects
    for player in game.players:
        player.draw(screen, game.particles)

    for enemy in game.enemies:
        enemy.draw(screen)

    for bullet in game.enemy_bullets:
        bullet.draw(screen)

    for powerup in game.powerups:
        powerup.draw(screen)

    for particle in game.particles:
        particle.draw(screen)

    for dn in game.damage_numbers:
        dn.draw(screen)

    # Draw UI
    draw_ui(screen, game)
    draw_crosshair(screen, pygame.mouse.get_pos(), game.combat.hitmarker_timer > 0,
                   game.weapon_system.crosshair_spread)

    if game.state == STATE_GAME_OVER:
        draw_game_over(screen, game)
    elif game.state == STATE_UPGRADE and game.pending_upgrades:
        draw_upgrade_menu(screen, game.pending_upgrades, game.upgrade_hovered)

    pygame.display.flip()

pygame.quit()
sys.exit()
