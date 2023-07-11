import pygame
from constants import *


class Chest():
    def __init__(self, x, y, name= 'tresure'):
        self.x = x
        self.y = y
        self.name = name
        self.closed = True
        self.size = 10
        self.text = 'this only opens when all switches are opened'
    
    def try_opening(self,switches):
        if all(switch.state == True for switch in switches):
            self.closed = False

    @staticmethod
    def chest_behaviour(chests,switches,window):
        for chest in chests:
            chest.try_opening(switches)
            if chest.closed == True:
                pygame.draw.rect(window, PINK, (chest.x, chest.y, chest.size, chest.size))
            else:
                pygame.draw.rect(window, GREEN, (chest.x, chest.y, chest.size, chest.size))