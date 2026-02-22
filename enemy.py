import pygame
import random
import os
from spaceship import SpaceShip
from constants import ENEMY_TYPES, ENEMY_IMAGE_PATHS, ENEMY_SHOT_IMAGE_PATHS, ENEMY_WIDTH, ENEMY_HEIGHT


class Enemy(SpaceShip):
    def __init__(self, x, y, color='blue', level=1):
        props = ENEMY_TYPES[color]
        super().__init__(x, y, props['health'], ENEMY_WIDTH, ENEMY_HEIGHT)
        self.color = color
        self.base_speed = props['speed']
        # velocidad vertical, se escala con el nivel
        self.speed = self.base_speed + (level - 1) * 0.02
        self.base_score = props.get('score', 10)
        self.shot_rate = props.get('shot_rate', 0.01)

        # Cargar imagenes si existen
        try:
            img_path = ENEMY_IMAGE_PATHS.get(color)
            if img_path and os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.image = None

        try:
            shot_path = ENEMY_SHOT_IMAGE_PATHS.get(color)
            if shot_path and os.path.exists(shot_path):
                self.bullet_img = pygame.image.load(shot_path).convert_alpha()
        except Exception:
            self.bullet_img = None

        # Movimiento horizontal aleatorio inicial
        self.dx = random.choice([-1, 1]) * (0.5 + random.random() * 1.5)
        # Cooldown para disparo: convertido desde shot_rate a frames
        # Si shot_rate es p(probabilidad/frame), 1/shot_rate ~= frames entre disparos
        try:
            base_cd = int(1.0 / float(self.shot_rate))
        except Exception:
            base_cd = 200
        # Usar cooldown base grande para evitar spam; reducir ligeramente por nivel
        self.shoot_cooldown_max = max(25, base_cd - int(level * 1.0))
        self.shoot_cooldown = random.randint(0, self.shoot_cooldown_max)

    def move(self, screen_width):
        # Movimiento vertical constante
        self.y += self.speed

        # Movimiento horizontal; rebotar en bordes
        self.x += self.dx
        if self.x < 0:
            self.x = 0
            self.dx *= -1
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width
            self.dx *= -1

        # Pequeñas variaciones aleatorias para hacer el movimiento más orgánico
        if random.random() < 0.01:
            self.dx *= -1

    def shoot(self, level=1):
        # Disparo basado en cooldown por enemigo; llamar cada frame desde game loop
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            bw = max(4, int(self.width * 0.12))
            bh = max(8, int(self.height * 0.4))
            bx = self.x + (self.width - bw) / 2
            by = self.y + self.height
            dy = 6 + (level * 0.02)
            # reset cooldown; permitir que niveles altos disparen un poco más seguido
            self.shoot_cooldown = max(15, int(self.shoot_cooldown_max * max(0.7, 1.0 - level * 0.005)))
            return self.shoot_bullet_dict(bx, by, bw, bh, dy)
        return None


class EnemyWave:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies = []

    def create_wave(self, level):
        # Cantidad se incrementa lentamente con el nivel
        base = 3
        additional = min(level // 1, 20)
        amount = base + additional + random.randint(5, max(20, level // 5))
        amount = min(amount, 80)

        self.enemies = []
        for i in range(amount):
            color = random.choice(list(ENEMY_TYPES.keys()))
            x = random.randint(10, max(10, self.screen_width - ENEMY_WIDTH - 10))
            y = random.randint(-1500, -50)  # aparecen por encima en distintas alturas
            enemy = Enemy(x, y, color=color, level=level)
            # Dar variación horizontal según color
            if color == 'blue':
                enemy.dx *= 0.6
            elif color == 'green':
                enemy.dx *= 1.1
            elif color == 'purple':
                enemy.dx *= 1.6

            self.enemies.append(enemy)

        return self.enemies

    def update(self, level):
        for e in self.enemies[:]:
            e.move(self.screen_width)
            # Si salen de la pantalla por abajo, los dejamos para que el juego detecte la condición
            if e.y > self.screen_height + 50:
                # mantenerlos, game.py decide si es game over al colisionar con jugador o llegar abajo
                pass

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.is_alive()]

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
