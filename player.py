import pygame
import os
from spaceship import SpaceShip
from constants import PLAYER_MAX_BULLETS, PLAYER_SHOOT_COOLDOWN, PLAYER_RELOAD_TIME


class Player(SpaceShip):
    """
    Clase Player: Nave del jugador con control, disparos y cooldown
    Hereda de SpaceShip
    """
    
    def __init__(self, x, y, health, width, height, speed=6):
        """
        Args:
            x (int|float): Posición x inicial.
            y (int|float): Posición y inicial.
            health (int): Puntos de vida iniciales.
            width (int): Ancho de la nave.
            height (int): Alto de la nave.
            speed (int): Velocidad de movimiento.
        """
        super().__init__(x, y, health, width, height)
        self.speed = speed
        # Cargador y recarga
        self.magazine_size = PLAYER_MAX_BULLETS
        self.current_ammo = self.magazine_size
        # Tiempo para recargar 1 proyectil (frames)
        self.reload_time_per_bullet = PLAYER_RELOAD_TIME
        self.reload_counter = 0

        # Cooldown mejorado para disparos
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = PLAYER_SHOOT_COOLDOWN  # Frames entre disparos

        # Velocidad de las balas
        self.bullet_speed = 12
    
    def set_image(self, image_path):
        """Cargar la imagen del jugador"""
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.mask = pygame.mask.from_surface(self.image)
        except pygame.error as e:
            print(f"Error al cargar imagen del jugador: {e}")
    
    def set_bullet_image(self, bullet_path):
        """Cargar la imagen de las balas"""
        try:
            self.bullet_img = pygame.image.load(bullet_path).convert_alpha()
        except pygame.error as e:
            print(f"Error al cargar imagen de bala: {e}")
    
    def move_left(self, screen_width):
        """Mover a la izquierda sin salir de la pantalla"""
        if self.x > 0:
            self.x -= self.speed
    
    def move_right(self, screen_width):
        """Mover a la derecha sin salir de la pantalla"""
        if self.x + self.width < screen_width:
            self.x += self.speed
    
    def update(self, screen_width):
        """Actualizar estado del jugador (cooldown de disparo)"""
        # Disminuir cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Actualizar posición de balas
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            # Eliminar balas fuera de pantalla
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        # Recarga gradual: si no hay munición completa, recargar con el contador
        if self.current_ammo < self.magazine_size:
            self.reload_counter += 1
            if self.reload_counter >= self.reload_time_per_bullet:
                self.reload_counter = 0
                self.current_ammo += 1
    
    def shoot(self):
        """Disparar si el cooldown lo permite"""
        if self.shoot_cooldown <= 0 and self.current_ammo > 0:
            # Tamaño de bala proporcional al ancho de la nave
            bw = max(4, int(self.width * 0.12))
            bh = max(8, int(self.height * 0.5))
            bullet = {
                'x': self.x + (self.width - bw) / 2,  # Centro de la nave
                'y': self.y - bh,
                'width': bw,
                'height': bh,
                'active': True,
            }
            self.bullets.append(bullet)
            self.shoot_cooldown = self.shoot_cooldown_max
            # consumir munición del cargador
            self.current_ammo = max(0, self.current_ammo - 1)
            # reset reload counter para comenzar a recargar cuando quede vacío
            if self.current_ammo < self.magazine_size and self.reload_counter == 0:
                self.reload_counter = 0
            return True
        return False
    
    def increase_difficulty(self):
        """Aumentar dificultad reduciendo cooldown entre disparos"""
        # Aumentar el cooldown para hacer el juego más difícil (máx 60)
        self.shoot_cooldown_max = min(60, self.shoot_cooldown_max + 1)
    
    def draw_bullets(self, window):
        """Dibujar las balas del jugador"""
        for bullet in self.bullets:
            if self.bullet_img:
                # Escalar la imagen de la bala al tamaño de la bala actual
                try:
                    img = pygame.transform.scale(self.bullet_img, (int(bullet['width']), int(bullet['height'])))
                    window.blit(img, (bullet['x'], bullet['y']))
                except Exception:
                    window.blit(self.bullet_img, (bullet['x'], bullet['y']))
            else:
                # Dibujar un rectángulo si no hay imagen
                pygame.draw.rect(window, (255, 255, 0), 
                               (bullet['x'], bullet['y'], bullet['width'], bullet['height']))
    
    def get_bullet_rect(self, bullet_index):
        """Obtener el rectángulo de una bala específica"""
        if bullet_index < len(self.bullets):
            bullet = self.bullets[bullet_index]
            return pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])
        return None
