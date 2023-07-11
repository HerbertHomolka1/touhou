import pygame

your_size = 25
drone_distance = 200

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
PINK = (255,192,203)

# Set up the walls
wall_thickness = 20

window_width, window_height = 1600, 900

window = pygame.display.set_mode((window_width, window_height))