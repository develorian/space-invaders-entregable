# ============== CONFIGURACIÓN DE PANTALLA ==============
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# ============== CONFIGURACIÓN DEL JUGADOR ==============
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_SPEED = 6
PLAYER_HEALTH = 3  # Vidas iniciales
PLAYER_BULLET_SPEED = 12
PLAYER_MAX_BULLETS = 5
PLAYER_SHOOT_COOLDOWN = 10  # Frames entre disparos (más lento para mayor dificultad)

# ============== CONFIGURACIÓN DE ENEMIGOS ==============
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 40

# Tipos de enemigos y sus propiedades:
# - weak: Salud baja, velocidad baja, puntuación baja
# - medium: Salud media, velocidad media, puntuación media
# - strong: Salud alta, velocidad alta, puntuación alta
ENEMY_TYPES = {
    'blue': {
        'health': 10,
        'speed': .8,
        'score': 10,
        'shot_rate': 0.01,
    },
    'green': {
        'health': 20,
        'speed': 1,
        'score': 25,
        'shot_rate': 0.02,
    },
    'purple': {
        'health': 30,
        'speed': 1.2,
        'score': 50,
        'shot_rate': 0.035,
    }
}

# ============== CONFIGURACIÓN DE JUEGO ==============
INITIAL_LIVES = 3
MAX_LEVEL = 100
GAME_FONT_SIZE = 36
HUD_FONT_SIZE = 24

# ============== CONFIGURACIÓN DE COLORES ==============
COLOR_BACKGROUND = (0, 0, 20)      # Azul oscuro
COLOR_TEXT = (255, 255, 255)        # Blanco
COLOR_LIVES = (255, 0, 0)           # Rojo para corazones
COLOR_ENEMY_WEAK = (100, 200, 255)  # Azul
COLOR_ENEMY_MEDIUM = (0, 255, 0)    # Verde
COLOR_ENEMY_STRONG = (255, 0, 0)    # Rojo

# ============== CONFIGURACIÓN DE ASSETS ==============
PLAYER_IMAGE_PATH = 'assets/img/player/spaceship.png'
PLAYER_BULLET_IMAGE_PATH = 'assets/img/player/bullet.png'
HEART_IMAGE_PATH = 'assets/img/ui/heart.png'  # Imagen de corazón para vidas

# Enemigos
ENEMY_IMAGE_PATHS = {
    'blue': 'assets/img/enemies/enemy_blue_image.png',
    'green': 'assets/img/enemies/enemy_green_image.png',
    'purple': 'assets/img/enemies/enemy_purple_image.png',
}

ENEMY_SHOT_IMAGE_PATHS = {
    'blue': 'assets/img/enemies/shot_blue_image.png',
    'green': 'assets/img/enemies/shot_green_image.png',
    'purple': 'assets/img/enemies/shot_purple_image.png',
}
