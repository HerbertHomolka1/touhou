import pygame
from pygame.locals import *
import math
from constants import *
from queue import PriorityQueue
import heapq  
import csv
from switch_class import Switch
from chest_class import Chest
from area_class import Area
from game_class import Game
from player_class import Player
from enemy_class import HumanGuard, BasicMonster, MilitaryDrone
from character_class import Character
from projectile_class import Projectile
from node_class import Node 



class Equipment:
    def __init__(self, bonus):
        self.bonus = bonus


class PowerRing(Equipment):
    def __init__(self):
        super().__init__({'h': 3, 'mana_regen': 2, 'max_mana_per_night': 5})


class StatusEffect:
    def __init__(self, bonus={}):
        self.bonus = bonus


class Bind(StatusEffect):
    def __init__(self):
        super().__init__({'speed':-50,'strength':-2})


bind = Bind()




class Level():
    levels = []
    def __init__(self, requirements, lvl,layout):
        self.requirements = requirements
        self.lvl = lvl
        self.layout = layout
    def lvlup(self):
        if self.requirements:
            Level.levels.pop(0)




#####################################################################
#####################################################################
#####################################################################


#####################################################################
#####################################################################
#####################################################################


#####################################################################
#####################################################################
#####################################################################

# Initialize Pygame
pygame.init()

print('start')

# Set up the display


pygame.display.set_caption("MyGame")


# Set up the main character

you = Player()

you.rect = pygame.Rect(you.x,you.y,you.size, you.size)

# Set up the enemy

enemies = []
projectiles = []

    
# Create a list to store the walls
walls = []
switches = []
chests = []
areas = []

# Iterate over the grid and create walls based on the CSV contents
# Initialize variables
# Convert CSV data to a list of grid coordinates

grid,grid_coordinates = Game.get_grid_from_csv()

walls = Game.setup_walls(grid,grid_coordinates,switches,chests,enemies)

         


# Game loop
running = True
clock = pygame.time.Clock()

while running:
 

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            you.shoot(projectiles)
 

    # Get the current state of the keyboard
    keys = pygame.key.get_pressed()
    
    # Update the player's position based on the pressed keys

    if 'Bind' in you.status:
        you.attempt_escape(keys)
    else:
        you.control_your_movement(keys,walls,you)    # Update the enemy's position to move towards the player

    you.immunity_check_and_setup()


    Character.enemy_behaviour(enemies, you, walls,projectiles)

    # Draw the background
    window.fill((255, 255, 255))
    
    # draw the walls
    for wall in walls:
        pygame.draw.rect(window, GRAY, wall)

    # Draw the player
    if you.teleport_countdown > 0:
        pygame.draw.rect(window, GREEN, (you.x, you.y, your_size, your_size))
    else:
        pygame.draw.rect(window, BLUE, (you.x, you.y, your_size, your_size))

    # Draw the enemy
    for enemy in enemies:
        pygame.draw.rect(window, RED, (enemy.x, enemy.y, enemy.size, enemy.size))
    
    Switch.switch_behaviour(switches,you,window)

    Chest.chest_behaviour(chests,switches,window)

    # area gives you a damage over time, think fire, poison gas etc. the one i set up is for test

    a = Area(600,450,100,1/30)
    areas = []
    areas += [a]

    Area.area_behaviour(areas, you,window)

    Projectile.projectile_behaviour(projectiles,enemies,you,walls,bind) # draw projectile, check if it hits anything etc

    you.countdown() # related to shooting? change name
    
    you.check_for_and_activate_spells(keys)

    Game.bottom_text_render(you,enemies,chests,projectiles) # render what the enemies are saying

    # Update the display
    pygame.display.update()

    # Control the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()