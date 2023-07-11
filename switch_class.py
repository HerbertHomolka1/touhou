import pygame
from constants import *

class Switch():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = False
        self.size = 10
    
    def switch(self):
        self.state = True
    
    @staticmethod
    def switch_behaviour(switches,you,window):
        for switch in switches:
            if switch.state == True:
                pygame.draw.rect(window, GREEN, (switch.x, switch.y, switch.size, switch.size))
            else:
                pygame.draw.rect(window, (140,110,23), (switch.x, switch.y, switch.size, switch.size))
            
            if switch.rect.colliderect(you):
                switch.switch()