import pygame
import sys
import random
import time
import os

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Movimiento del Personaje con Enemigos Móviles")

# Rutas de las imágenes relativas al directorio del script
current_dir = os.path.dirname(__file__)
background_image_path = os.path.join(current_dir, 'imagenes', 'espacio.jpg')
nave_image_path = os.path.join(current_dir, 'imagenes', 'nave.png')
meteoro_image_path = os.path.join(current_dir, 'imagenes', 'meteoro.png')

# Cargar imagen de fondo del espacio
background_image = pygame.image.load(background_image_path).convert_alpha()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Tamaño del personaje y velocidad de movimiento
CHAR_RADIUS = 25  # Radio del personaje
CHAR_SPEED = 5

# Tamaño del enemigo y velocidad de movimiento (mismo tamaño que el personaje)
ENEMY_RADIUS = 25  # Radio del enemigo
ENEMY_SPEED = 2

# Función para verificar colisiones circulares
def check_collision_circles(sprite1, sprite2):
    distance_squared = (sprite1.rect.centerx - sprite2.rect.centerx) ** 2 + (sprite1.rect.centery - sprite2.rect.centery) ** 2
    radius_sum_squared = (sprite1.radius + sprite2.radius) ** 2
    return distance_squared < radius_sum_squared

# Clase para el personaje
class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cargar imagen PNG para el personaje
        self.original_image = pygame.image.load(nave_image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (CHAR_RADIUS * 2, CHAR_RADIUS * 2))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.radius = CHAR_RADIUS
        self.is_alive = True
        self.start_time = time.time()  # Tiempo de inicio del juego
        self.direction = 0  # Dirección inicial (en grados)

    def update(self, keys):
        if self.is_alive:
            # Movimiento con las flechas
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= CHAR_SPEED
                self.direction = 90  # Girar hacia la izquierda
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += CHAR_SPEED
                self.direction = 270  # Sin rotación (hacia la derecha)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.rect.y -= CHAR_SPEED
                self.direction = 0  # Girar hacia arriba
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.rect.y += CHAR_SPEED
                self.direction = 180  # Girar hacia abajo

            # Limitar el movimiento dentro de la pantalla
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

            # Rotar la imagen según la dirección
            self.image = pygame.transform.rotate(self.original_image, self.direction)

    def get_elapsed_time(self):
        """Devuelve el tiempo transcurrido desde el inicio del juego en minutos y segundos."""
        elapsed_time_seconds = int(time.time() - self.start_time)
        minutes = elapsed_time_seconds // 60
        seconds = elapsed_time_seconds % 60
        return minutes, seconds

    def die(self):
        """Marca al personaje como muerto."""
        self.is_alive = False

    def respawn(self):
        """Respawn del personaje."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.is_alive = True
        self.start_time = time.time()  # Reiniciar el tiempo de juego

# Clase para los enemigos móviles
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cargar imagen PNG para el enemigo
        self.original_image = pygame.image.load(meteoro_image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (ENEMY_RADIUS * 2, ENEMY_RADIUS * 2))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - ENEMY_RADIUS * 2)
        self.rect.y = random.randrange(SCREEN_HEIGHT - ENEMY_RADIUS * 2)
        self.radius = ENEMY_RADIUS
        self.dx = random.choice([-1, 1]) * ENEMY_SPEED
        self.dy = random.choice([-1, 1]) * ENEMY_SPEED

    def update(self):
        # Mover el enemigo
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Rebotar en los bordes de la pantalla
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.dx = -self.dx
            self.image = pygame.transform.flip(self.image, True, False)  # Cambiar la dirección horizontal
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.dy = -self.dy
            self.image = pygame.transform.flip(self.image, False, True)  # Cambiar la dirección vertical

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    character = Character()
    all_sprites = pygame.sprite.Group()
    all_enemies = pygame.sprite.Group()

    all_sprites.add(character)

    # Crear enemigos móviles
    for _ in range(10):  # Cantidad fija de enemigos
        enemy = Enemy()
        all_sprites.add(enemy)
        all_enemies.add(enemy)

    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and not character.is_alive:
                # Si el personaje está muerto y se presiona cualquier tecla, reiniciar el juego
                character.respawn()

        # Obtener las teclas presionadas
        keys = pygame.key.get_pressed()

        # Actualizar el personaje si está vivo
        if character.is_alive:
            character.update(keys)

        # Actualizar los enemigos
        all_enemies.update()

        # Verificar colisiones con los enemigos si el personaje está vivo
        if character.is_alive:
            for enemy in all_enemies:
                if check_collision_circles(character, enemy):
                    character.die()

        # Dibujar fondo del espacio
        screen.blit(background_image, (0, 0))

        # Dibujar todos los sprites
        all_sprites.draw(screen)

        # Mostrar mensaje de reinicio si el personaje está muerto
        if not character.is_alive:
            font = pygame.font.Font(None, 48)
            restart_text = font.render("Presiona cualquier tecla para reiniciar", True, (255, 255, 255))
            text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, text_rect)

        # Mostrar tiempo transcurrido en pantalla si el personaje está vivo
        if character.is_alive:
            minutes, seconds = character.get_elapsed_time()
            font = pygame.font.Font(None, 36)
            time_text = font.render(f"Tiempo: {minutes} min {seconds} seg", True, (255, 255, 255))
            screen.blit(time_text, (10, 10))

        pygame.display.flip()

        # Controlar la velocidad de actualización
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Iniciar el juego
if __name__ == "__main__":
    main()
