import pygame


class SpaceShip:
    """Clase base para `Player` y `Enemy`.

    Provee: posición, vida, imagen, balas simples y utilidades de dibujado/colisión.
    """
    def __init__(self, x, y, health, width, height):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.width = width
        self.height = height

        self.image = None
        self.bullet_img = None

        # Lista de balas: dicts con keys x,y,w,h,dy,img
        self.bullets = []

        # Cooldown para disparo (frames)
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 1

        # Máscara para colisiones pixel-perfect
        self.mask = None

    def set_image(self, image_path_or_surface):
        if isinstance(image_path_or_surface, str):
            self.image = pygame.image.load(image_path_or_surface).convert_alpha()
        else:
            self.image = image_path_or_surface
        self.mask = pygame.mask.from_surface(self.image)

    def set_bullet_image(self, image_path_or_surface):
        if isinstance(image_path_or_surface, str):
            self.bullet_img = pygame.image.load(image_path_or_surface).convert_alpha()
        else:
            self.bullet_img = image_path_or_surface

    def draw(self, window):
        if self.image:
            window.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        return self.health <= 0

    def is_alive(self):
        return self.health > 0

    def update_cooldown(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot_bullet_dict(self, x, y, width, height, dy):
        return {'x': x, 'y': y, 'width': width, 'height': height, 'dy': dy, 'img': self.bullet_img}

    def draw_bullets(self, window):
        for b in self.bullets:
            if b.get('img'):
                img = b['img']
                window.blit(img, (b['x'], b['y']))
            else:
                pygame.draw.rect(window, (255, 255, 0), (b['x'], b['y'], b['width'], b['height']))

    def update_bullets(self, screen_height):
        for b in self.bullets[:]:
            b['y'] += b['dy']
            if b['y'] < -50 or b['y'] > screen_height + 50:
                self.bullets.remove(b)