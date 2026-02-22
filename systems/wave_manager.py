from config.settings import WIDTH, STATE_UPGRADE
from entities.enemy import Enemy, EnemyType
from systems.spawner import spawn_enemy
from systems.upgrade_system import roll_upgrades


def next_wave(game):
    game.wave += 1
    game.enemies_per_wave += 2
    game.enemies_spawned_this_wave = 0
    game.spawn_interval = max(60, game.spawn_interval - 3)

    # Boss spawn every 5 waves
    if game.wave % 5 == 0:
        boss = Enemy(WIDTH // 2, -100, game.wave, EnemyType.TANK)
        boss.health = int(boss.health * 2)
        boss.max_health = boss.health
        boss.size = 70
        game.enemies.append(boss)

    # Trigger upgrade selection screen
    game.pending_upgrades = roll_upgrades(3)
    game.upgrade_hovered = 0
    game.state = STATE_UPGRADE


def handle_spawning(game):
    game.spawn_timer += 1
    if game.spawn_timer >= game.spawn_interval:
        if game.enemies_spawned_this_wave < game.enemies_per_wave:
            spawn_enemy(game)
            game.spawn_timer = 0
        elif len(game.enemies) == 0:
            next_wave(game)
            game.spawn_timer = 0
