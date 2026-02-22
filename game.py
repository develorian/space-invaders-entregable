import pygame
import random
import os
from player import Player
from enemy import EnemyWave
from constants import *


class Game:
    def __init__(self, font, FPS, lives, window, screen_width, screen_height, clock=None):
        self.font = font
        self.hud_font = pygame.font.Font(None, HUD_FONT_SIZE)
        self.HEIGHT = screen_height
        self.WIDTH = screen_width
        self.FPS = FPS
        self.window = window
        self.clock = clock if clock else pygame.time.Clock()

        # Estado
        self.level = 1
        self.score = 0
        self.game_over = False
        self.victory = False
        self.game_time = 0

        # Jugador
        self.player = Player(
            x=self.WIDTH // 2 - PLAYER_WIDTH // 2,
            y=self.HEIGHT - 80,
            health=lives,
            width=PLAYER_WIDTH,
            height=PLAYER_HEIGHT,
            speed=PLAYER_SPEED,
        )
        self.load_player_images()

        # Oleadas
        self.enemy_wave = EnemyWave(self.WIDTH, self.HEIGHT)
        self.enemies = []
        self.enemy_bullets = []

        # UI
        self.heart_image = None
        self.load_ui_images()

        self.sounds = {}
        self.load_sounds()

        self.create_wave()

    def load_player_images(self):
        try:
            self.player.set_image(PLAYER_IMAGE_PATH)
            self.player.set_bullet_image(PLAYER_BULLET_IMAGE_PATH)
        except Exception as e:
            print("Error cargando imágenes del jugador:", e)

    def load_ui_images(self):
        try:
            if os.path.exists(HEART_IMAGE_PATH):
                self.heart_image = pygame.image.load(HEART_IMAGE_PATH).convert_alpha()
                self.heart_image = pygame.transform.scale(self.heart_image, (20, 20))
        except Exception as e:
            print("Error cargando UI:", e)

    def load_sounds(self):
        pass

    def create_wave(self):
        self.enemies = self.enemy_wave.create_wave(self.level)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.victory:
                    self.player.shoot()
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def update(self):
        if self.game_over or self.victory:
            return

        self.game_time += 1 / self.FPS

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left(self.WIDTH)
        if keys[pygame.K_RIGHT]:
            self.player.move_right(self.WIDTH)

        self.player.update(self.WIDTH)
        self.enemy_wave.update(self.level)

        # actualizar balas enemigas
        self.update_enemy_bullets()

        # enemigos disparan
        self.enemy_random_shoot()

        # colisiones
        self.check_collisions()

        # condiciones de juego
        self.check_game_conditions()

    def update_enemy_bullets(self):
        for b in self.enemy_bullets[:]:
            b['y'] += b.get('dy', 6)
            if b['y'] > self.HEIGHT + 50:
                self.enemy_bullets.remove(b)

    def enemy_random_shoot(self):
        # Limitar cuántos enemigos intentan disparar por frame y tope de balas en pantalla
        alive = self.enemy_wave.get_alive_enemies()
        if not alive:
            return

        # número de intentos de disparo por frame (aprox 1 por 6 enemigos, mínimo 1 y máximo 6)
        max_attempts = min(6, max(1, len(alive) // 6))
        shooters = random.sample(alive, k=min(len(alive), max_attempts))

        # tope global de balas enemigas en pantalla
        max_enemy_bullets = min(30, 5 + self.level * 2)

        for shooter in shooters:
            if len(self.enemy_bullets) >= max_enemy_bullets:
                break
            b = shooter.shoot(self.level)
            if b:
                self.enemy_bullets.append(b)

    def check_collisions(self):
        player_rect = self.player.get_rect()
        alive_enemies = self.enemy_wave.get_alive_enemies()

        # balas jugador -> enemigos
        for bi in range(len(self.player.bullets) - 1, -1, -1):
            bullet = self.player.bullets[bi]
            br = pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])
            for e in alive_enemies[:]:
                er = e.get_rect()
                if br.colliderect(er):
                    # remover bala
                    if bi < len(self.player.bullets):
                        self.player.bullets.pop(bi)
                    e.take_damage(25)
                    if not e.is_alive():
                        self.enemy_wave.remove_enemy(e)
                        self.score += e.base_score * self.level
                    break

        # balas enemigas -> jugador
        for b in self.enemy_bullets[:]:
            br = pygame.Rect(b['x'], b['y'], b['width'], b['height'])
            if br.colliderect(player_rect):
                self.enemy_bullets.remove(b)
                self.player.take_damage(1)
                break

        # colision directa enemigos -> jugador
        for e in alive_enemies[:]:
            # Si un enemigo choca con el jugador, quitarle vida al jugador
            if e.get_rect().colliderect(player_rect):
                self.enemy_wave.remove_enemy(e)
                self.player.take_damage(1)
                # No terminar el juego aquí; check_game_conditions decidirá si las vidas se agotaron

    def check_game_conditions(self):
        if not self.player.is_alive():
            self.game_over = True
            return
        alive = self.enemy_wave.get_alive_enemies()
        if len(alive) == 0:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.player.increase_difficulty()
        if self.level <= MAX_LEVEL:
            self.create_wave()
        else:
            self.victory = True

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.game_over = False
        self.victory = False
        self.game_time = 0
        self.player.health = self.player.max_health
        self.player.x = self.WIDTH // 2 - PLAYER_WIDTH // 2
        self.player.y = self.HEIGHT - 80
        self.player.bullets = []
        self.player.shoot_cooldown_max = PLAYER_SHOOT_COOLDOWN
        self.enemy_bullets = []
        self.enemy_wave = EnemyWave(self.WIDTH, self.HEIGHT)
        self.create_wave()

    def draw(self):
        self.window.fill(COLOR_BACKGROUND)
        # estrellas
        random.seed(42)
        for i in range(80):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            pygame.draw.circle(self.window, (200, 200, 200), (x, y), 1)

        if not self.game_over and not self.victory:
            self.player.draw(self.window)
            self.player.draw_bullets(self.window)

            for e in self.enemy_wave.enemies:
                e.draw(self.window)

            for b in self.enemy_bullets:
                if b.get('img'):
                    self.window.blit(b['img'], (b['x'], b['y']))
                else:
                    pygame.draw.rect(self.window, (255, 100, 0), (b['x'], b['y'], b['width'], b['height']))

        self.draw_hud()

        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()

    def draw_hud(self):
        y_offset = 10
        score_text = self.hud_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.window.blit(score_text, (10, y_offset))
        level_text = self.hud_font.render(f"Level: {self.level}/{MAX_LEVEL}", True, COLOR_TEXT)
        self.window.blit(level_text, (10, y_offset + 35))
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.hud_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, COLOR_TEXT)
        self.window.blit(time_text, (10, y_offset + 70))
        self.draw_lives_hud(y_offset)
        self.draw_bullets_hud(y_offset)

    def draw_lives_hud(self, y_offset):
        hearts_x = self.WIDTH - 150
        hearts_y = y_offset
        for i in range(int(self.player.health)):
            if self.heart_image:
                self.window.blit(self.heart_image, (hearts_x + i * 25, hearts_y))
            else:
                pygame.draw.circle(self.window, COLOR_LIVES, (hearts_x + i * 25 + 8, hearts_y + 5), 5)
                pygame.draw.circle(self.window, COLOR_LIVES, (hearts_x + i * 25 + 12, hearts_y + 5), 5)
                pygame.draw.polygon(self.window, COLOR_LIVES,
                                    [(hearts_x + i * 25, hearts_y + 8),
                                     (hearts_x + i * 25 + 20, hearts_y + 8),
                                     (hearts_x + i * 25 + 10, hearts_y + 18)])
        lives_label = self.hud_font.render(f"Lives:", True, COLOR_TEXT)
        self.window.blit(lives_label, (hearts_x - 70, hearts_y - 5))

    def draw_bullets_hud(self, y_offset):
        bullets_x = self.WIDTH - 150
        bullets_y = y_offset + 50
        max_bullets = self.player.max_bullets
        current_bullets = len(self.player.bullets)
        b_img = None
        try:
            b_img = self.player.bullet_img
            if b_img:
                b_img = pygame.transform.scale(b_img, (12, 18))
        except Exception:
            b_img = None
        for i in range(max_bullets):
            slot_x = bullets_x + i * 18
            if i < max_bullets - current_bullets:
                if b_img:
                    self.window.blit(b_img, (slot_x, bullets_y))
                else:
                    pygame.draw.rect(self.window, (255, 255, 0), (slot_x, bullets_y, 12, 18))
            else:
                if b_img:
                    dark = b_img.copy()
                    dark.fill((80, 80, 80, 120), special_flags=pygame.BLEND_RGBA_MULT)
                    self.window.blit(dark, (slot_x, bullets_y))
                else:
                    pygame.draw.rect(self.window, (100, 100, 0), (slot_x, bullets_y, 12, 18))
        bullets_label = self.hud_font.render(f"Ammo:", True, COLOR_TEXT)
        self.window.blit(bullets_label, (bullets_x - 70, bullets_y - 5))

    def draw_game_over(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.window.blit(overlay, (0, 0))
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        level_text = self.font.render(f"Level Reached: {self.level}", True, COLOR_TEXT)
        restart_text = self.hud_font.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
        self.window.blit(game_over_text,
                         (self.WIDTH // 2 - game_over_text.get_width() // 2, self.HEIGHT // 2 - 100))
        self.window.blit(score_text,
                         (self.WIDTH // 2 - score_text.get_width() // 2, self.HEIGHT // 2 - 20))
        self.window.blit(level_text,
                         (self.WIDTH // 2 - level_text.get_width() // 2, self.HEIGHT // 2 + 20))
        self.window.blit(restart_text,
                         (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 80))

    def draw_victory(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 200))
        self.window.blit(overlay, (0, 0))
        victory_text = self.font.render("VICTORY!", True, (0, 255, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        level_text = self.font.render(f"Level Completed: {self.level}", True, COLOR_TEXT)
        restart_text = self.hud_font.render("Press R to play again or ESC to quit", True, COLOR_TEXT)
        self.window.blit(victory_text,
                         (self.WIDTH // 2 - victory_text.get_width() // 2, self.HEIGHT // 2 - 100))
        self.window.blit(score_text,
                         (self.WIDTH // 2 - score_text.get_width() // 2, self.HEIGHT // 2 - 20))
        self.window.blit(level_text,
                         (self.WIDTH // 2 - level_text.get_width() // 2, self.HEIGHT // 2 + 20))
        self.window.blit(restart_text,
                         (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 80))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
