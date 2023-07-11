import pygame
from constants import *

class Projectile:
    def __init__(self, x, y, direction_x, direction_y, speed,owner):
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.owner = owner
        self.rect = pygame.Rect(self.x,self.y,8,8)
        self.damage = 10

    def update(self,you,walls,projectiles,bind):
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed
        self.rect = pygame.Rect(self.x,self.y,8,8)
        
        if self.rect.colliderect(you):    
            if self.owner != you:    
                if you.immunity['immunity'] == False:
                    
                    you.inflict_status(bind)
                try:
                    projectiles.remove(self)
                except ValueError:
                    pass

        cond1 = self.x > 1600 or self.x <0
        cond2 = self.y > 900 or self.y <0
        if cond1 or cond2:
            
                
            if self in projectiles:
                projectiles.remove(self)
                

        for wall in walls:
            if self.rect.colliderect(wall):
                
                if self in projectiles:
                    projectiles.remove(self)
                
    def draw(self):
        
        pygame.draw.circle(window, (34, 100, 160), (int(self.x), int(self.y)), 8)

    @staticmethod
    def projectile_behaviour(projectiles,enemies,you,walls,bind):
        for projectile in projectiles:
            for enemy in enemies:
                if enemy.rect.colliderect(projectile):
                    if projectile.owner not in enemies:
                        enemy.hp -= projectile.damage
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                        projectiles.remove(projectile)
            projectile.update(you,walls,projectiles,bind)
            projectile.draw()




