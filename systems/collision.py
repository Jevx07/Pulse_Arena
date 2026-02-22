from config.settings import ACCENT_COLOR
from entities.particle import Particle
from entities.powerup import PowerupType


def check_collisions(game):
    player = game.players[0]
    player_rect = player.get_rect()

    for enemy in game.enemies[:]:
        if player_rect.colliderect(enemy.get_rect()):
            enemy_center = enemy.get_center()
            player_center = player.get_center()
            direction = (
                enemy_center[0] - player_center[0],
                enemy_center[1] - player_center[1],
            )

            if player.take_damage(enemy.damage, direction):
                game.screen_shake = 12
                game.combat.combo = 0
                for _ in range(15):
                    game.particles.append(
                        Particle(
                            player.x + player.size // 2,
                            player.y + player.size // 2,
                            ACCENT_COLOR,
                            velocity_range=4,
                        )
                    )

    for bullet in game.enemy_bullets[:]:
        bullet_pos = bullet.get_pos()
        if player_rect.collidepoint(bullet_pos):
            direction = (bullet.dx, bullet.dy)
            if player.take_damage(8, direction):
                game.screen_shake = 8
                game.combat.combo = 0
            game.enemy_bullets.remove(bullet)

    for powerup in game.powerups[:]:
        if player_rect.colliderect(powerup.get_rect()):
            player.apply_powerup(powerup.type)

            if powerup.type == PowerupType.AMMO:
                game.current_ammo = game.max_ammo

            for _ in range(15):
                game.particles.append(
                    Particle(
                        powerup.x,
                        powerup.y,
                        powerup.colors[powerup.type],
                        velocity_range=4,
                    )
                )

            game.powerups.remove(powerup)

