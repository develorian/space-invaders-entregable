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
        # velocidad vertical, se escala con el nivel (pequeño incremento por nivel)
        self.speed = self.base_speed * (1.0 + (level - 1) * 0.03)
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
        # Reducir cooldown por nivel para que disparen más a medida que avanza
        self.shoot_cooldown_max = max(12, base_cd - int(level * 4))
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
        # almacenar cantidad de la última oleada generada
        self.prev_amount = None

    def create_wave(self, level):
        # Determinar cantidad: nivel 1 fija en 10; niveles siguientes = prev + (1..5)
        if self.prev_amount is None:
            amount = 10
        else:
            amount = self.prev_amount + random.randint(1, 5)

        self.enemies = []
        # controlar ventana de aparición: nivel 1 aparece más cerca de la parte superior;
        # niveles superiores se dispersan más para aparecer poco a poco
        if level <= 1:
            max_offset = 150
        else:
            max_offset = min(2000, 300 + level * 120)
        for i in range(amount):
            color = random.choice(list(ENEMY_TYPES.keys()))
            x = random.randint(10, max(10, self.screen_width - ENEMY_WIDTH - 10))
            y = random.randint(-max_offset, -50)  # aparecen por encima en distintas alturas
            enemy = Enemy(x, y, color=color, level=level)
            # Dar variación horizontal según color
            if color == 'blue':
                enemy.dx *= 0.6
            elif color == 'green':
                enemy.dx *= 1.1
            elif color == 'purple':
                enemy.dx *= 1.6

            self.enemies.append(enemy)

        # guardar la cantidad generada para la siguiente oleada
        self.prev_amount = len(self.enemies)
        return self.enemies

    def update(self, level):
        for e in self.enemies[:]:
            e.move(self.screen_width)
            # Si salen de la pantalla por abajo, eliminarlos de la oleada
            if e.y > self.screen_height + 50:
                try:
                    self.enemies.remove(e)
                except ValueError:
                    pass

    def get_last_wave_count(self):
        return self.prev_amount

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.is_alive()]

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
