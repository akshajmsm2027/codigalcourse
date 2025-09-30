import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Load assets
car_width, car_height = 50, 100
player_car = pygame.image.load("car.png")  # Replace with your car image
player_car = pygame.transform.scale(player_car, (car_width, car_height))

# Obstacle settings
obstacle_width, obstacle_height = 50, 100
obstacle_color = RED

# Player car position
player_x = WIDTH // 2 - car_width // 2
player_y = HEIGHT - car_height - 10
player_speed = 5

# Obstacle position and speed
obstacle_x = random.randint(0, WIDTH - obstacle_width)
obstacle_y = -obstacle_height
obstacle_speed = 5

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - car_width:
        player_x += player_speed

    # Draw player car
    screen.blit(player_car, (player_x, player_y))

    # Obstacle movement
    obstacle_y += obstacle_speed
    if obstacle_y > HEIGHT:
        obstacle_y = -obstacle_height
        obstacle_x = random.randint(0, WIDTH - obstacle_width)
        score += 1  # Increase score when obstacle is passed

    # Draw obstacle
    pygame.draw.rect(screen, obstacle_color, (obstacle_x, obstacle_y, obstacle_width, obstacle_height))

    # Collision detection
    if (player_x < obstacle_x + obstacle_width and
        player_x + car_width > obstacle_x and
        player_y < obstacle_y + obstacle_height and
        player_y + car_height > obstacle_y):
        print("Game Over!")
        running = False

    # Display score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
