# indian_bike_like.py
# Simple 2D bike-driving game inspired by "Indian Bike Driving".
# Requires pygame: pip install pygame

import pygame
import random
import math
from pygame.locals import *
#ryrtryne5zne4z
# --- Config
WIDTH, HEIGHT = 800, 600
FPS = 60

ROAD_WIDTH = 420
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
ROAD_X = (WIDTH - ROAD_WIDTH) // 2

BIKE_WIDTH = 36
BIKE_HEIGHT = 60

OBSTACLE_MIN_GAP = 700
OBSTACLE_MAX_GAP = 1400

MAX_SPEED = 12
ACCEL_RATE = 0.12
BRAKE_RATE = 0.3
FRICTION = 0.02
STEER_RATE = 5  # degrees per frame at base

NITRO_BOOST = 6
NITRO_DURATION = 0.9  # seconds
NITRO_COOLDOWN = 3.0  # seconds

# Colors
ROAD_COLOR = (60, 60, 60)
GRASS_COLOR = (30, 140, 40)
LANE_MARK_COLOR = (230, 230, 230)
BACKGROUND_COLOR = (135, 206, 235)
BIKE_COLOR = (220, 30, 30)
OBST_COLOR = (10, 10, 10)
HUD_COLOR = (20, 20, 20)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bike Run — Inspired")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, italic=False)

# Helper functions
def draw_text(surf, text, x, y, size=22, color=(255,255,255)):
    f = pygame.font.SysFont("Arial", size)
    r = f.render(text, True, color)
    surf.blit(r, (x, y))

class Bike:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 140
        self.speed = 0.0
        self.angle = 0.0  # lean angle for visual
        self.score = 0
        self.lives = 3

        self.nitro_time = 0.0
        self.nitro_ready_in = 0.0

    @property
    def rect(self):
        return pygame.Rect(self.x - BIKE_WIDTH//2, self.y - BIKE_HEIGHT//2, BIKE_WIDTH, BIKE_HEIGHT)

    def update(self, dt, keys):
        # speed controls
        if keys[K_UP]:
            self.speed += ACCEL_RATE * (1 + 0.3 * (self.nitro_time > 0))
        else:
            self.speed -= FRICTION

        if keys[K_DOWN]:
            self.speed -= BRAKE_RATE

        # clamp speed
        top = MAX_SPEED + (NITRO_BOOST if self.nitro_time > 0 else 0)
        self.speed = max(0, min(self.speed, top))

        # steering depends on speed
        steer_mult = 1 + (self.speed / MAX_SPEED) * 0.5
        if keys[K_LEFT]:
            self.x -= STEER_RATE * steer_mult
            self.angle = max(-25, self.angle - 3)
        elif keys[K_RIGHT]:
            self.x += STEER_RATE * steer_mult
            self.angle = min(25, self.angle + 3)
        else:
            # settle angle
            if self.angle > 0:
                self.angle -= 2
            elif self.angle < 0:
                self.angle += 2

        # nitro
        if keys[K_SPACE] and self.nitro_ready_in <= 0 and self.nitro_time <= 0:
            self.nitro_time = NITRO_DURATION
            self.nitro_ready_in = NITRO_COOLDOWN + NITRO_DURATION

        # nitro timers
        if self.nitro_time > 0:
            self.nitro_time -= dt
            if self.nitro_time < 0:
                self.nitro_time = 0
        if self.nitro_ready_in > 0:
            self.nitro_ready_in -= dt
            if self.nitro_ready_in < 0:
                self.nitro_ready_in = 0

        # keep on road
        left_bound = ROAD_X + BIKE_WIDTH // 2
        right_bound = ROAD_X + ROAD_WIDTH - BIKE_WIDTH // 2
        if self.x < left_bound:
            self.x = left_bound
            self.speed *= 0.6
        if self.x > right_bound:
            self.x = right_bound
            self.speed *= 0.6

class Obstacle:
    def __init__(self, x, y, obs_type='car'):
        self.x = x
        self.y = y
        self.type = obs_type
        self.width = random.randint(40, 70)
        self.height = random.randint(60, 80) if obs_type=='car' else random.randint(30, 40)

    def rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)

class Road:
    def __init__(self):
        self.offset = 0  # vertical offset for scrolling
        self.obstacles = []
        self._distance_since_last = 0
        self.upcoming_gap = random.randint(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP)
        self.total_distance = 0

    def update(self, dt, bike_speed):
        # scroll the road
        pixels = bike_speed * 12  # speed to pixels mapping
        self.offset += pixels * dt * FPS
        self.total_distance += pixels * dt * FPS
        self._distance_since_last += pixels * dt * FPS

        # spawn obstacles based on distance
        if self._distance_since_last > self.upcoming_gap:
            lane = random.randrange(LANE_COUNT)
            lane_center = ROAD_X + lane * LANE_WIDTH + LANE_WIDTH // 2
            x_jitter = random.randint(-LANE_WIDTH//4, LANE_WIDTH//4)
            obs_x = lane_center + x_jitter
            obs_y = -120  # spawn above screen
            self.obstacles.append(Obstacle(obs_x, obs_y))
            self._distance_since_last = 0
            self.upcoming_gap = random.randint(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP)

        # move obstacles down relative to road movement
        for ob in self.obstacles:
            ob.y += pixels * dt * FPS

        # remove passed obstacles
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 200]

    def draw(self, surf):
        # grass
        surf.fill(BACKGROUND_COLOR)
        pygame.draw.rect(surf, GRASS_COLOR, (0, 0, ROAD_X, HEIGHT))
        pygame.draw.rect(surf, GRASS_COLOR, (ROAD_X + ROAD_WIDTH, 0, WIDTH - (ROAD_X + ROAD_WIDTH), HEIGHT))

        # road
        pygame.draw.rect(surf, ROAD_COLOR, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

        # lane marks
        for i in range(1, LANE_COUNT):
            mx = ROAD_X + i * LANE_WIDTH
            dash_h = 30
            gap = 18
            y = - (self.offset % (dash_h + gap))
            while y < HEIGHT:
                pygame.draw.rect(surf, LANE_MARK_COLOR, (mx - 3, y, 6, dash_h))
                y += dash_h + gap

        # side stripes
        pygame.draw.rect(surf, LANE_MARK_COLOR, (ROAD_X+4, 0, 6, HEIGHT))
        pygame.draw.rect(surf, LANE_MARK_COLOR, (ROAD_X + ROAD_WIDTH - 10, 0, 6, HEIGHT))

        #
