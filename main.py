import pygame
import sys
from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    """Función principal para iniciar el juego"""
    # Inicializar Pygame
    pygame.init()
    
    # Crear ventana
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders 🚀")
    
    # Cargar fuentes
    font = pygame.font.Font(None, 36)
    
    # Crear instancia del juego
    game = Game(
        font=font,
        FPS=FPS,
        lives=3,
        window=screen,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT
    )
    
    # Ejecutar el juego
    game.run()
    
    # Salir de Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()