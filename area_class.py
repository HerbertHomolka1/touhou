import pygame
from constants import *
from game_class import Game

class Area():
    def __init__(self, x,y,radius,damage):
        self.x =x
        self.y = y
        self.radius = radius
        self.damage = damage


    @staticmethod
    def area_behaviour(areas, you,window):
        for area in areas:
            circle_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            circle_color = pygame.Color(71, 136, 0, 100)
            circle_radius = 100
            pygame.draw.circle(circle_surface, circle_color, (100, 100), circle_radius)
            window.blit(circle_surface, (area.x, area.y))
            area.deal_damage(you)
        
    
    def deal_damage(self,to_whom):
        if Game.calculate_distance((to_whom.x + to_whom.size/2 ,to_whom.y+to_whom.size/2),(self.x+self.radius,self.y+self.radius)) < self.radius + to_whom.size/2:
            to_whom.receive_damage(self.damage)