import pygame

from config.settings import (
    STATE_GAME_OVER,
    STATE_PLAYING,
    STATE_UPGRADE,
    WIDTH,
    HEIGHT,
)
from core.event_bus import EventBus
from core.modes.survival_mode import SurvivalMode
from core.stats_tracker import StatsTracker
from entities.bullet import EnemyBullet
from entities.player import Player
from entities.particle import Particle
from systems.collision import check_collisions
from systems.combat import CombatSystem
from systems.weapon_system import WeaponSystem, RIFLE


class GameManager:
    def __init__(self):
        self.players = [Player(WIDTH // 2 - 22, HEIGHT // 2 - 22, player_id=0)]
        self.enemies = []
        self.enemy_bullets = []
        self.particles = []
        self.damage_numbers = []
        self.powerups = []

        self.score = 0
        self.kills = 0
        self.wave = 1

        # --- Weapon system (owns firing, ammo, fire rate) ---
        self.weapon_system = WeaponSystem(RIFLE)

        # Ammo state mirrors current weapon (read by HUD + CombatSystem)
        self.max_ammo = RIFLE.max_ammo
        self.current_ammo = self.max_ammo
        self.reload_time = RIFLE.reload_time
        self.last_reload = 0
        self.is_reloading = False

        # Temporary mouse pos store for burst drip-feed
        self._last_mouse_pos = (WIDTH // 2, HEIGHT // 2)

        # --- Wave spawning state ---
        self.spawn_timer = 0
        self.spawn_interval = 120
        self.enemies_per_wave = 5
        self.enemies_spawned_this_wave = 0

        self.state = STATE_PLAYING
        self.screen_shake = 0

        # --- P3: Upgrade state ---
        self.pending_upgrades: list = []
        self.upgrade_hovered: int = 0

        # --- Event bus (pub/sub for future systems) ---
        self.event_bus = EventBus()

        # --- Mode (plug-and-play game modes) ---
        self.active_mode = SurvivalMode()

        # --- P6: Retention / stats ---
        self.stats = StatsTracker()

        # --- Combat sub-system ---
        self.combat = CombatSystem()

    def reload(self):
        if not self.is_reloading and self.current_ammo < self.max_ammo:
            self.is_reloading = True
            self.last_reload = pygame.time.get_ticks()

    def update(self):
        if self.state not in (STATE_PLAYING,):
            return

        current_time = pygame.time.get_ticks()

        # Reload completion
        if self.is_reloading:
            if current_time - self.last_reload >= self.reload_time:
                self.current_ammo = self.max_ammo
                self.is_reloading = False

        # Player movement
        keys = pygame.key.get_pressed()
        for player in self.players:
            player.update(keys)

        # Enemy AI + shooting
        player_center = self.players[0].get_center()
        for enemy in self.enemies[:]:
            should_shoot, direction = enemy.update(player_center, self.enemies)
            if should_shoot and direction:
                enemy_center = enemy.get_center()
                self.enemy_bullets.append(
                    EnemyBullet(
                        enemy_center[0],
                        enemy_center[1],
                        direction[0],
                        direction[1],
                    )
                )

        # Entity updates
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)

        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_expired():
                self.powerups.remove(powerup)

        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

        for dn in self.damage_numbers[:]:
            dn.update()
            if dn.is_dead():
                self.damage_numbers.remove(dn)

        self.active_mode.update(self)
        check_collisions(self)

        # Tick weapon system (burst queue + crosshair decay)
        self.weapon_system.update(self)

        # Delegate combat timer ticks to CombatSystem
        self.combat.update(self)

        previous_alive = self.players[0].is_alive()
        if not previous_alive and self.state != STATE_GAME_OVER:
            self.state = STATE_GAME_OVER
            self.stats.commit_run(self)   # fires once (guarded inside StatsTracker)

        if self.screen_shake > 0:
            self.screen_shake -= 1

    def restart(self):
        old_stats = self.stats  # preserve stats tracker across restarts
        self.__init__()
        self.stats = old_stats
        self.stats.reset_guard()
