import pygame
import random
import os
from player import Player
from enemy import EnemyWave
from constants import *
from score import Puntajes


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
        self.kills = 0
        self.game_over = False
        self.victory = False
        self.game_time = 0
        # estado de menú inicial
        self.in_menu = True

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

        # Temporizador para pantalla de inicio de nivel
        self.level_start_duration = int(2 * self.FPS)  # 2 segundos
        self.level_start_timer = 0

        # UI
        self.heart_image = None
        self.load_ui_images()

        self.sounds = {}
        self.load_sounds()

        # Puntajes
        try:
            self.score_db = Puntajes()
        except Exception:
            self.score_db = None

        # input nombre en game over
        self.name_input = ""
        self.name_submitted = False
        self.show_scores_overlay = False

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
        # Inicializar el mixer si no está inicializado
        try:
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception:
                    # Falló init del mixer; seguir sin sonido
                    print("Warning: pygame.mixer no pudo inicializarse; sonido deshabilitado")
                    return

            sounds_dir = os.path.join('assets', 'sounds')
            bg_path = os.path.join(sounds_dir, 'background_song.mp3')
            expl_path = os.path.join(sounds_dir, 'explosion.wav')

            # Música de fondo (loop)
            if os.path.exists(bg_path):
                try:
                    pygame.mixer.music.load(bg_path)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print("Error cargando música de fondo:", e)
            else:
                print(f"Background music not found: {bg_path}")

            # Efecto de explosión
            if os.path.exists(expl_path):
                try:
                    self.sounds['explosion'] = pygame.mixer.Sound(expl_path)
                    self.sounds['explosion'].set_volume(0.6)
                except Exception as e:
                    print("Error cargando sonido de explosión:", e)
            else:
                print(f"Explosion sound not found: {expl_path}")

        except Exception as e:
            print("Error en load_sounds:", e)

    def create_wave(self):
        self.enemies = self.enemy_wave.create_wave(self.level)
        # Mostrar HUD de inicio de nivel y pausar acciones durante un breve tiempo
        self.level_start_timer = self.level_start_duration
        # reset contador de inicio de nivel visual
        self.name_input = ""
        self.name_submitted = False
        self.show_scores_overlay = False

    def handle_events(self):
        for event in pygame.event.get():
            # si estamos en menú, manejar entradas de menú
            if self.in_menu:
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # comprobar botones si existen
                    try:
                        if getattr(self, 'start_button_rect', None) and self.start_button_rect.collidepoint((mx, my)):
                            self.in_menu = False
                            return True
                        if getattr(self, 'exit_button_rect', None) and self.exit_button_rect.collidepoint((mx, my)):
                            return False
                    except Exception:
                        pass
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.in_menu = False
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
                continue
            # manejar pantalla de Game Over y de registro de puntaje
            if self.game_over:
                # si aún no se registró nombre, mostrar panel de registro primero
                if not self.name_submitted:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        try:
                            # submit registro
                            if getattr(self, 'scoreentry_submit_rect', None) and self.scoreentry_submit_rect.collidepoint((mx, my)):
                                if self.name_input.strip() and self.score_db:
                                    try:
                                        self.score_db.add_score(self.name_input.strip(), self.kills, self.game_time, self.level, self.score)
                                        self.name_submitted = True
                                    except Exception:
                                        pass
                            # skip registro -> ir al panel de Game Over
                            if getattr(self, 'scoreentry_skip_rect', None) and self.scoreentry_skip_rect.collidepoint((mx, my)):
                                self.name_submitted = True
                        except Exception:
                            pass
                    if event.type == pygame.KEYDOWN:
                        # reiniciar con R sin agregar la letra al input
                        if event.key == pygame.K_r:
                            self.reset_game()
                            return True
                        if event.key == pygame.K_BACKSPACE:
                            self.name_input = self.name_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.name_input.strip() and self.score_db:
                                try:
                                    self.score_db.add_score(self.name_input.strip(), self.kills, self.game_time, self.level, self.score)
                                    self.name_submitted = True
                                except Exception:
                                    pass
                        else:
                            if len(self.name_input) < 20 and event.unicode.isprintable():
                                self.name_input += event.unicode
                else:
                    # panel principal de Game Over: reiniciar, salir, ver puntajes
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        try:
                            if getattr(self, 'gameover_restart_rect', None) and self.gameover_restart_rect.collidepoint((mx, my)):
                                self.reset_game()
                                return True
                            if getattr(self, 'gameover_exit_rect', None) and self.gameover_exit_rect.collidepoint((mx, my)):
                                return False
                            if getattr(self, 'gameover_view_rect', None) and self.gameover_view_rect.collidepoint((mx, my)):
                                self.show_scores_overlay = not self.show_scores_overlay
                            if getattr(self, 'show_scores_overlay', False) and getattr(self, 'scores_close_rect', None) and self.scores_close_rect.collidepoint((mx, my)):
                                self.show_scores_overlay = False
                        except Exception:
                            pass
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

        # Si estamos en la introducción del nivel, contar el timer y pausar actualizaciones
        if getattr(self, 'level_start_timer', 0) > 0:
            self.level_start_timer -= 1
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
        max_attempts = min(6, max(1, len(alive) // 8))
        shooters = random.sample(alive, k=min(len(alive), max_attempts))

        # tope global de balas enemigas en pantalla (aumenta por nivel)
        max_enemy_bullets = min(60, 5 + self.level * 2)

        for shooter in shooters:
            if len(self.enemy_bullets) >= max_enemy_bullets:
                break
            # ajustar probabilidad de disparo por enemigo según su shot_rate y el nivel
            try:
                base_prob = getattr(shooter, 'shot_rate', 0.01)
                adj_prob = base_prob * max(1.0, 1.0 + (self.level - 1) * 0.08)
                if random.random() < adj_prob:
                    b = shooter.shoot(self.level)
                else:
                    b = None
            except Exception:
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
                    # reproducir sonido de explosión si está disponible
                    try:
                        snd = self.sounds.get('explosion')
                        if snd:
                            snd.play()
                    except Exception:
                        pass
                    if not e.is_alive():
                        self.enemy_wave.remove_enemy(e)
                        self.score += e.base_score * self.level
                        self.kills += 1
                    break

        # balas enemigas -> jugador
        for b in self.enemy_bullets[:]:
            br = pygame.Rect(b['x'], b['y'], b['width'], b['height'])
            if br.colliderect(player_rect):
                self.enemy_bullets.remove(b)
                self.player.take_damage(1)
                # reproducir sonido de explosión si está disponible
                try:
                    snd = self.sounds.get('explosion')
                    if snd:
                        snd.play()
                except Exception:
                    pass
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
        # aumentar la dificultad del jugador (si aplica)
        try:
            self.player.increase_difficulty()
        except Exception:
            pass

        # cada 3 niveles, aumentar un poco la velocidad de movimiento del jugador
        try:
            if self.level % 3 == 0:
                # incrementar en 0.5, con un tope para evitar velocidad excesiva
                self.player.speed = min(getattr(self.player, 'speed', 6) + 0.5, 12)
        except Exception:
            pass

        # generar la nueva oleada (juego infinito)
        self.create_wave()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.kills = 0
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
        # reset HUD timer para el primer nivel
        self.level_start_timer = self.level_start_duration
        self.name_input = ""
        self.name_submitted = False
        self.show_scores_overlay = False

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
        # Si estamos mostrando la pantalla de inicio de nivel, oscurecer y dibujar HUD
        if getattr(self, 'level_start_timer', 0) > 0:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.window.blit(overlay, (0, 0))
            # Texto de nivel y advertencia con emojis
            lvl_text = self.font.render(f"LEVEL {self.level}", True, (255, 255, 0))
            warn_text = self.hud_font.render("⚠️👾 CUIDADO!! Viene una oleada de aliens 👾⚠️", True, (255, 180, 0))
            self.window.blit(lvl_text, (self.WIDTH // 2 - lvl_text.get_width() // 2, self.HEIGHT // 2 - 60))
            self.window.blit(warn_text, (self.WIDTH // 2 - warn_text.get_width() // 2, self.HEIGHT // 2))

        self.draw_hud()

        # Mostrar pantalla de Game Over / Victory cuando corresponda
        if self.game_over:
            if not self.name_submitted:
                self.draw_score_entry()
            else:
                self.draw_game_over()
            if self.show_scores_overlay:
                self.draw_scores_overlay()
        elif self.victory:
            self.draw_victory()

    def draw_menu(self):
        # Fondo
        self.window.fill(COLOR_BACKGROUND)
        # Dibujar imagen de la nave del jugador arriba del título si existe
        try:
            if self.player.image:
                img = pygame.transform.scale(self.player.image, (120, 96))
                self.window.blit(img, (self.WIDTH // 2 - img.get_width() // 2, 40))
        except Exception:
            pass

        # Título grande
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Space Invader 2026", True, (255, 255, 0))
        subtitle = self.hud_font.render("    (Millenium)", True, (200, 200, 200))
        self.window.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 160))
        self.window.blit(subtitle, (self.WIDTH // 2 - subtitle.get_width() // 2, 220))

        # Botones
        btn_w, btn_h = 220, 48
        start_rect = pygame.Rect(self.WIDTH // 2 - btn_w // 2, 300, btn_w, btn_h)
        exit_rect = pygame.Rect(self.WIDTH // 2 - btn_w // 2, 360, btn_w, btn_h)
        self.start_button_rect = start_rect
        self.exit_button_rect = exit_rect

        pygame.draw.rect(self.window, (50, 150, 50), start_rect)
        pygame.draw.rect(self.window, (150, 50, 50), exit_rect)

        start_text = self.hud_font.render("Iniciar Juego", True, (255, 255, 255))
        exit_text = self.hud_font.render("Salir", True, (255, 255, 255))
        self.window.blit(start_text, (start_rect.centerx - start_text.get_width() // 2, start_rect.centery - start_text.get_height() // 2))
        self.window.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))

        # Ayuda pequeña
        hint = self.hud_font.render("Presiona Enter o haz click en Iniciar", True, (180, 180, 180))
        self.window.blit(hint, (self.WIDTH // 2 - hint.get_width() // 2, 430))

        # Mostrar la mayor puntuación en el menú, si existe
        try:
            if self.score_db:
                rows = self.score_db.get_all_scores()
                if rows:
                    top = max(rows, key=lambda r: r[4])
                    name, kills, play_time, level, score, ts = top
                    top_txt = self.hud_font.render(f"Mayor puntuación: {name}   {score}   (Nivel {level})", True, (220, 220, 220))
                    self.window.blit(top_txt, (self.WIDTH // 2 - top_txt.get_width() // 2, self.HEIGHT - 60))
        except Exception:
            pass

        if self.game_over:
            if not self.name_submitted:
                self.draw_score_entry()
            else:
                self.draw_game_over()
        elif self.victory:
            self.draw_victory()

    def draw_hud(self):
        y_offset = 10
        # Left column: Score / Level / Kills / Time
        score_text = self.hud_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.window.blit(score_text, (10, y_offset))
        level_text = self.hud_font.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.window.blit(level_text, (10, y_offset + 30))
        kills_text = self.hud_font.render(f"Kills: {self.kills}", True, COLOR_TEXT)
        self.window.blit(kills_text, (10, y_offset + 60))
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.hud_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, COLOR_TEXT)
        self.window.blit(time_text, (10, y_offset + 90))

        # Right column: Lives and Ammo aligned to top (same y_offset)
        self.draw_lives_hud(y_offset)
        self.draw_bullets_hud(y_offset)

    def draw_lives_hud(self, y_offset):
        # Mostrar vidas en la esquina superior derecha (alineadas con y_offset)
        hearts_x = self.WIDTH - 280
        hearts_y = y_offset
        for i in range(int(self.player.health)):
            if self.heart_image:
                self.window.blit(self.heart_image, (hearts_x + i * 30, hearts_y))
            else:
                pygame.draw.circle(self.window, COLOR_LIVES, (hearts_x + i * 30 + 8, hearts_y + 8), 6)
                pygame.draw.circle(self.window, COLOR_LIVES, (hearts_x + i * 30 + 18, hearts_y + 8), 6)
                pygame.draw.polygon(self.window, COLOR_LIVES,
                                    [(hearts_x + i * 30, hearts_y + 14),
                                     (hearts_x + i * 30 + 32, hearts_y + 14),
                                     (hearts_x + i * 30 + 16, hearts_y + 30)])
        lives_label = self.hud_font.render(f"Lives:", True, COLOR_TEXT)
        self.window.blit(lives_label, (hearts_x - 80, hearts_y))

    def draw_bullets_hud(self, y_offset):
        # Mostrar munición al lado derecho superior, alineada con lives
        bullets_x = self.WIDTH - 140
        bullets_y = y_offset
        max_bullets = getattr(self.player, 'magazine_size', self.player.max_bullets if hasattr(self.player, 'max_bullets') else 5)
        current_bullets = getattr(self.player, 'current_ammo', len(self.player.bullets))
        b_img = None
        try:
            b_img = self.player.bullet_img
            if b_img:
                b_img = pygame.transform.scale(b_img, (12, 18))
        except Exception:
            b_img = None
        for i in range(max_bullets):
            slot_x = bullets_x + i * 18
            if i < current_bullets:
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
        self.window.blit(bullets_label, (bullets_x - 70, bullets_y))

    def draw_game_over(self):
        # Full-screen dark overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.window.blit(overlay, (0, 0))

        # Panel central
        panel_w, panel_h = min(760, self.WIDTH - 80), min(420, self.HEIGHT - 120)
        panel_x = self.WIDTH // 2 - panel_w // 2
        panel_y = self.HEIGHT // 2 - panel_h // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.window, (18, 18, 18), panel)
        pygame.draw.rect(self.window, (200, 200, 200), panel, 2)

        pad = 20
        y = panel_y + pad
        # Title
        game_over_text = self.font.render("GAME OVER", True, (220, 40, 40))
        self.window.blit(game_over_text, (panel_x + panel_w // 2 - game_over_text.get_width() // 2, y))
        y += game_over_text.get_height() + 12

        # Summary (centered)
        score_text = self.hud_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        level_text = self.hud_font.render(f"Level Reached: {self.level}", True, COLOR_TEXT)
        kills_text = self.hud_font.render(f"Enemies Killed: {self.kills}", True, COLOR_TEXT)
        time_text = self.hud_font.render(f"Time: {int(self.game_time)}s", True, COLOR_TEXT)
        col_x = panel_x + pad
        self.window.blit(score_text, (col_x, y))
        self.window.blit(kills_text, (col_x + 320, y))
        y += score_text.get_height() + 8
        self.window.blit(level_text, (col_x, y))
        self.window.blit(time_text, (col_x + 320, y))
        y += level_text.get_height() + 18

        # Bottom buttons: View Scores / Restart / Exit
        btn_w, btn_h = 160, 44
        gap = 18
        total_w = btn_w * 3 + gap * 2
        start_x = panel_x + panel_w // 2 - total_w // 2

        view_rect = pygame.Rect(start_x, panel_y + panel_h - btn_h - pad, btn_w, btn_h)
        restart_rect = pygame.Rect(start_x + (btn_w + gap), panel_y + panel_h - btn_h - pad, btn_w, btn_h)
        exit_rect = pygame.Rect(start_x + 2 * (btn_w + gap), panel_y + panel_h - btn_h - pad, btn_w, btn_h)

        self.gameover_view_rect = view_rect
        self.gameover_restart_rect = restart_rect
        self.gameover_exit_rect = exit_rect

        pygame.draw.rect(self.window, (120, 120, 120), view_rect)
        pygame.draw.rect(self.window, (60, 140, 60), restart_rect)
        pygame.draw.rect(self.window, (140, 60, 60), exit_rect)

        view_label = self.hud_font.render("Ver puntajes", True, (255, 255, 255))
        restart_label = self.hud_font.render("Reiniciar", True, (255, 255, 255))
        exit_label = self.hud_font.render("Salir", True, (255, 255, 255))

        self.window.blit(view_label, (view_rect.centerx - view_label.get_width() // 2, view_rect.centery - view_label.get_height() // 2))
        self.window.blit(restart_label, (restart_rect.centerx - restart_label.get_width() // 2, restart_rect.centery - restart_label.get_height() // 2))
        self.window.blit(exit_label, (exit_rect.centerx - exit_label.get_width() // 2, exit_rect.centery - exit_label.get_height() // 2))

        # Confirmation message if score was saved
        if self.name_submitted:
            ok = self.hud_font.render("Tus datos fueron guardados.", True, (0, 255, 0))
            self.window.blit(ok, (panel_x + panel_w // 2 - ok.get_width() // 2, panel_y + panel_h - btn_h - pad - 36))

    def draw_score_entry(self):
        # Full-screen dark overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.window.blit(overlay, (0, 0))

        # Panel central más compacto
        panel_w, panel_h = min(600, self.WIDTH - 120), min(300, self.HEIGHT - 200)
        panel_x = self.WIDTH // 2 - panel_w // 2
        panel_y = self.HEIGHT // 2 - panel_h // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.window, (16, 16, 16), panel)
        pygame.draw.rect(self.window, (200, 200, 200), panel, 2)

        pad = 16
        y = panel_y + pad
        title = self.font.render("REGISTRAR PUNTAJE", True, (255, 215, 0))
        self.window.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, y))
        y += title.get_height() + 12

        # Summary
        score_text = self.hud_font.render(f"Score: {self.score}    Level: {self.level}    Kills: {self.kills}", True, COLOR_TEXT)
        self.window.blit(score_text, (panel_x + pad, y))
        y += score_text.get_height() + 16

        # Input
        inp_w, inp_h = panel_w - pad * 2, 40
        inp_x = panel_x + pad
        inp_y = y
        inp_rect = pygame.Rect(inp_x, inp_y, inp_w, inp_h)
        pygame.draw.rect(self.window, (30, 30, 30), inp_rect)
        pygame.draw.rect(self.window, (160, 160, 160), inp_rect, 2)
        name_label = self.hud_font.render("Nombre:", True, COLOR_TEXT)
        self.window.blit(name_label, (inp_x, inp_y - 26))
        input_text = self.hud_font.render(self.name_input if self.name_input else "", True, COLOR_TEXT)
        self.window.blit(input_text, (inp_x + 8, inp_y + 6))
        y = inp_y + inp_h + 16

        # Instrucción: presionar Enter para registrar (solo input + Enter)
        hint = self.hud_font.render("Presiona Enter para registrar tu nombre (R = Reiniciar)", True, (200, 200, 200))
        self.window.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2, y))
        # No dibujamos botones; la entrada se realiza con teclado


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

    def draw_scores_overlay(self):
        # Full black background for scores
        self.window.fill((0, 0, 0))
        title = self.font.render("PUNTAJES", True, (255, 215, 0))
        self.window.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 20))

        if not self.score_db:
            err = self.hud_font.render("Base de datos no disponible.", True, (255, 100, 100))
            self.window.blit(err, (self.WIDTH // 2 - err.get_width() // 2, 120))
            return

        # obtener todos y ordenar por score descendente
        rows = self.score_db.get_all_scores()
        rows_sorted = sorted(rows, key=lambda r: r[4], reverse=True)

        # encabezado
        header = self.hud_font.render("#  Name          Kills   Time   Level   Score", True, (200, 200, 200))
        margin_x = 60
        y = 100
        self.window.blit(header, (margin_x, y))
        y += 36

        max_show = min(len(rows_sorted), 20)
        for idx in range(max_show):
            r = rows_sorted[idx]
            name, kills, play_time, level, score, ts = r
            rank = idx + 1
            line = f"{rank:2d}. {name[:12]:12}    {kills:3d}    {int(play_time):4d}s    {level:3d}    {score:6d}"
            txt = self.hud_font.render(line, True, (220, 220, 220))
            self.window.blit(txt, (margin_x, y))
            y += 28

        # close button bottom-right
        close_rect = pygame.Rect(self.WIDTH - 140, self.HEIGHT - 70, 120, 44)
        pygame.draw.rect(self.window, (140, 60, 60), close_rect)
        close_label = self.hud_font.render("Cerrar", True, (255, 255, 255))
        self.window.blit(close_label, (close_rect.centerx - close_label.get_width() // 2, close_rect.centery - close_label.get_height() // 2))
        self.scores_close_rect = close_rect

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if not running:
                break
            if self.in_menu:
                # dibujar menú especial
                self.draw_menu()
            else:
                self.update()
                self.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
