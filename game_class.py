import pygame
import csv
from constants import *
from switch_class import Switch
from chest_class import Chest
from enemy_class import HumanGuard, MilitaryDrone, BasicMonster
import math
from constants import *

class Game():

    @staticmethod
    def get_angle_and_distance(where_from,where_to):
        

        if type(where_from) != tuple:
            dx = where_from.x - where_to.x
            dy = where_from.y - where_to.y
        else:
            dx = where_from[0] - where_to.x
            dy = where_from[1] - where_to.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.atan2(dy, dx)

        return angle,distance

    @staticmethod
    def calculate_distance(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    @staticmethod
    def get_grid_from_csv():
        csv_file = "grid.csv"
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            grid = list(reader)
        grid_coordinates = []
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 'x':
                    grid_coordinates.append((x, y))
        return grid,grid_coordinates

    @staticmethod
    def setup_walls(grid,grid_coordinates,switches,chests,enemies):
        walls = []

        # Find horizontal walls
        for y in range(len(grid)):
            current_wall_start = None
            current_wall_end = None
            for x in range(len(grid[y])):
                if (x, y) in grid_coordinates:
                    if current_wall_start is None:
                        current_wall_start = (x, y)
                    current_wall_end = (x, y)
                else:
                    if current_wall_start is not None:
                        wall_width = current_wall_end[0] - current_wall_start[0] + 1
                        wall_height = current_wall_end[1] - current_wall_start[1] + 1
                        pos_x = current_wall_start[0] * wall_thickness
                        pos_y = current_wall_start[1] * wall_thickness
                        wall_rect = pygame.Rect(pos_x, pos_y, wall_width * wall_thickness, wall_thickness)
                        walls.append(wall_rect)
                        for i in range(current_wall_start[0], current_wall_end[0] + 1):
                            grid_coordinates.remove((i, y))
                        current_wall_start = None
                        current_wall_end = None

            if current_wall_start is not None:
                wall_width = current_wall_end[0] - current_wall_start[0] + 1
                wall_height = current_wall_end[1] - current_wall_start[1] + 1
                pos_x = current_wall_start[0] * wall_thickness
                pos_y = current_wall_start[1] * wall_thickness
                wall_rect = pygame.Rect(pos_x, pos_y, wall_width * wall_thickness, wall_thickness)
                walls.append(wall_rect)
                for i in range(current_wall_start[0], current_wall_end[0] + 1):
                    grid_coordinates.remove((i, y))

        # Find vertical walls
        for x in range(len(grid[0])):
            current_wall_start = None
            current_wall_end = None
            for y in range(len(grid)):
                if (x, y) in grid_coordinates:
                    if current_wall_start is None:
                        current_wall_start = (x, y)
                    current_wall_end = (x, y)
                else:
                    if current_wall_start is not None:
                        wall_width = wall_thickness
                        wall_height = current_wall_end[1] - current_wall_start[1] + 1
                        pos_x = current_wall_start[0] * wall_thickness
                        pos_y = current_wall_start[1] * wall_thickness
                        wall_rect = pygame.Rect(pos_x, pos_y, wall_thickness, wall_height * wall_thickness)
                        walls.append(wall_rect)
                        for i in range(current_wall_start[1], current_wall_end[1] + 1):
                            grid_coordinates.remove((x, i))
                        current_wall_start = None
                        current_wall_end = None

            if current_wall_start is not None:
                wall_width = wall_thickness
                wall_height = current_wall_end[1] - current_wall_start[1] + 1
                pos_x = current_wall_start[0] * wall_thickness
                pos_y = current_wall_start[1] * wall_thickness
                wall_rect = pygame.Rect(pos_x, pos_y, wall_thickness, wall_height * wall_thickness)
                walls.append(wall_rect)
                for i in range(current_wall_start[1], current_wall_end[1] + 1):
                    grid_coordinates.remove((x, i))

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell in ['m','g','d']:
                    if cell == 'm':
                        enemy = BasicMonster()
                    if cell == 'g':
                        enemy = HumanGuard()
                    if cell == 'd':
                        enemy = MilitaryDrone()
                    enemy.x = x * wall_thickness
                    enemy.y = y * wall_thickness
                    enemy.rect = pygame.Rect(enemy.x,enemy.y,enemy.size,enemy.size)
                    enemies.append(enemy)
                
                elif cell == 's': # check for switches
                    pos_x = x * wall_thickness
                    pos_y = y * wall_thickness
                    switch = Switch(pos_x,pos_y)
                    switch.rect = pygame.Rect(pos_x, pos_y, wall_thickness, wall_thickness)
                    switches.append(switch)
                elif cell == 'c': # check for chests
                    pos_x = x * wall_thickness
                    pos_y = y * wall_thickness
                    chest = Chest(pos_x,pos_y)
                    chest.rect = pygame.Rect(pos_x, pos_y, wall_thickness, wall_thickness)
                    chests.append(chest)


        return walls # because walls = setup_walls()
    
    @staticmethod
    def bottom_text_render(you,enemies,chests,projectiles):
        font = pygame.font.Font(None, 36)
        text = font.render(str(you.immunity['immunity'])+str(you.status), True, (0, 0, 0))
    
        text_rect = text.get_rect()
        text_rect.center = (window_width -60, 40)
        window.blit(text, text_rect)
        text = font.render(str(you.teleport_countdown)+ '  ' + str(int(you.x)) + '  ' + str(int(you.y)), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (window_width -200, 40)
        window.blit(text, text_rect)
        text = font.render(str(len(projectiles)), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (window_width -360, 40)
        window.blit(text, text_rect)
        text = font.render(
            f'Your HP: {str(you.hp)}',
            True, 
            (0, 0, 0) 
            )
        text_rect = text.get_rect()
        text_rect.center = (window_width -400, 300+100)
        window.blit(text, text_rect)
        who_says = None
        for enemy in enemies + chests:
            if Game.calculate_distance((you.x,you.y),(enemy.x+enemy.size/2,enemy.y+enemy.size/2)) < 200:
                    who_says = enemy
                    break
        if who_says:
            Game.say_sth(who_says,who_says.text)

    @staticmethod
    def say_sth(who, what_says):

        # Set up the dialog box dimensions
        dialog_box_width = 900
        dialog_box_height = 100
        dialog_box_x = (window_width - dialog_box_width) // 2
        dialog_box_y = window_height - dialog_box_height - 50

        # Create the dialog box surface
        # Create the border surface
        border_surface = pygame.Surface((dialog_box_width + 10, dialog_box_height + 10))
        border_surface.fill((0, 0, 0))  # Fill with black color
        dialog_box_surface = pygame.Surface((dialog_box_width, dialog_box_height))
        dialog_box_surface.fill((255, 255, 255))  # Fill with white color
        dialog_box_rect = dialog_box_surface.get_rect()
        dialog_box_rect.topleft = (dialog_box_x, dialog_box_y)


        # Set up the font for the dialog box
        font = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)

        # Set up the text content
        text_content = what_says
        text_content2 = str(who.name)
        # Render the text onto the dialog box surface
        text_surface = font.render(text_content, True, (0, 0, 0))  # Render text with black color
        text_rect = text_surface.get_rect()
        text_rect.center = dialog_box_rect.center  # Position the text in the center of the dialog box

        text_surface2 = font_bold.render(text_content2, True, (0, 0, 0))  # Render text with black color
        text_rect2 = text_surface2.get_rect()
        text_rect2.center = (dialog_box_x + dialog_box_width/2, dialog_box_y+15)# Position the text in the center of the dialog box

        # Draw a border on the border surface
        pygame.draw.rect(border_surface, (255, 255, 255), border_surface.get_rect(), 4)  # White border with thickness 4

        # Position the border surface
        border_rect = border_surface.get_rect()
        border_rect.center = dialog_box_rect.center

        # Blit the border surface onto the screen
        window.blit(border_surface, border_rect.topleft)

        # Blit the dialog box surface onto the screen
        window.blit(dialog_box_surface, dialog_box_rect.topleft)

        # Blit the text surface onto the screen
        window.blit(text_surface, text_rect.topleft)
            # Blit the text surface onto the screen
        window.blit(text_surface2, text_rect2.topleft)







    # Generate a list of neighboring nodes for a given position
    @staticmethod
    def get_neighbors(position):
        x, y = position
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1),(x-1, y-1),(x+1, y-1),(x-1, y+1),(x+1, y+1)]  # Left, Right, Up, Down
        valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < window_width and 0 <= ny < window_height ]

        # Check if the current cxxoordinates contain an obstacle
        temp = pygame.Rect(x,y,70,70)
        for wall in walls:
            if temp.colliderect(wall):
                return []
        return valid_neighbors

