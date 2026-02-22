import random

from config.settings import WIDTH, HEIGHT
from entities.enemy import Enemy, EnemyType


def spawn_enemy(game):
    wave = game.wave

    if wave >= 11:
        # Full pool including Support
        enemy_type = random.choices(
            [EnemyType.RUSHER, EnemyType.TANK, EnemyType.SHOOTER,
             EnemyType.SWARM, EnemyType.HUNTER, EnemyType.SNIPER, EnemyType.SUPPORT],
            weights=[20, 10, 15, 10, 20, 15, 10],
        )[0]
    elif wave >= 8:
        # Snipers introduced
        enemy_type = random.choices(
            [EnemyType.RUSHER, EnemyType.TANK, EnemyType.SHOOTER,
             EnemyType.SWARM, EnemyType.HUNTER, EnemyType.SNIPER],
            weights=[25, 15, 15, 10, 20, 15],
        )[0]
    elif wave >= 5:
        # Hunters introduced
        enemy_type = random.choices(
            [EnemyType.RUSHER, EnemyType.TANK, EnemyType.SHOOTER, EnemyType.HUNTER],
            weights=[35, 15, 30, 20],
        )[0]
    else:
        # Waves 1–4: basics only
        enemy_type = random.choices(
            [EnemyType.RUSHER, EnemyType.SHOOTER],
            weights=[60, 40],
        )[0]

    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        x = random.randint(0, WIDTH - 50)
        y = -50
    elif edge == "bottom":
        x = random.randint(0, WIDTH - 50)
        y = HEIGHT + 50
    elif edge == "left":
        x = -50
        y = random.randint(0, HEIGHT - 50)
    else:
        x = WIDTH + 50
        y = random.randint(0, HEIGHT - 50)

    game.enemies.append(Enemy(x, y, game.wave, enemy_type))
    game.enemies_spawned_this_wave += 1
