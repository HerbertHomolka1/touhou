from character_class import Character
from pygame.locals import *
import pygame
import math

class Player(Character):
    def __init__(self):
        super().__init__(25,'MC', 50, 50, 2, 1, 10, None)
        self.mp = 1
        self.mana_regen = 1
        self.max_mana_per_night = 5
        self.h = 0
        self.learned_spells = set(['teleport','barrier'])
        self.teleport_countdown = 0
        self.stealth = False

    def dot(self):
        self.h += 2

    def gsm(self):
        self.h = 0
        self.mp += self.mana_regen

    def learn_spell(self, spell):
        spell_methods = [getattr(spell, method) for method in dir(spell) if callable(getattr(spell, method)) and not method.startswith("__")]
        self.learned_spells = self.learned_spells.union(spell_methods)

    def teleport(self, keys, walls):
        if 'teleport' in self.learned_spells:
            if keys[K_SPACE]:
                if self.teleport_countdown == 0:
                    change_x = 0
                    change_y = 0
                    if keys[K_RIGHT]:
                        self.x += 400
                        change_x = 1
                    elif keys[K_LEFT]:
                        self.x -= 400
                        change_x = -1
                    if keys[K_DOWN]:
                        self.y += 400
                        change_y = 1
                    elif keys[K_UP]:
                        self.y -= 400
                        change_y = -1

                    self.rect = pygame.Rect(self.x, self.y, 8, 8)
                    while any(self.rect.colliderect(wall) for wall in walls):
                        self.x -= 10 * change_x
                        self.y -= 10 * change_y
                        self.rect = pygame.Rect(self.x, self.y, 8, 8)
                        print([self.rect.colliderect(wall) for wall in walls].count(True))
                        self.original_x,self.original_y = self.x,self.y
                      
                        


                    if self.x< 0:
                        self.x = 11
                    elif self.x > 1600:
                        self.x = 1589
                    if self.y< 0:
                        self.y = 11
                    elif self.y> 900:
                        self.y = 889
            

                    self.teleport_countdown = 60
            if self.teleport_countdown > 0:
                self.teleport_countdown -= 1 

    def check_for_and_activate_spells(self,keys):
        if keys[K_i]:
            if 'barrier' in self.learned_spells:
                if self.immunity['immunity'] == False:
                    self.immunity_up()
        if keys[K_s]:
            self.stealth = not self.stealth

    def immunity_up(self):
        self.immunity['immunity'] = True
        you.immunity['duration'] = 300
    
    def immunity_check_and_setup(self):
        if self.immunity['duration']>0:
            self.immunity['duration'] -= 1
        if self.immunity['escape']>0:
            self.immunity['escape'] -= 1
        if self.immunity['duration'] ==0:
            self.immunity['immunity'] = False

    def shoot(self,projectiles):
        from game_class import Game
        
        pos = pygame.mouse.get_pos()

        angle, _ = Game.get_angle_and_distance(pos,self)
        if 'Bind' not in self.status:
            self.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles)   



    def control_your_movement(self,keys,walls,you):

        if (keys[K_LEFT] or keys[K_RIGHT]) and (keys[K_UP] or keys[K_DOWN]):
            modifier = math.sqrt(2)/2
        else:
            modifier = 1

        modifier *= 1.2

        your_speed = you.get_stats('speed')

        you.original_x = you.x
        you.original_y = you.y
        
        if keys[K_LEFT]:
            you.x -= your_speed *modifier
        if keys[K_RIGHT]:
            you.x += your_speed *modifier
        if keys[K_UP]:
            you.y -= your_speed *modifier
        if keys[K_DOWN]:
            you.y += your_speed *modifier
        

        you.rect = pygame.Rect(you.x, you.y, you.size, you.size)
        Character.avoid_wall_collision(you,walls)
        you.teleport(keys,walls)

    def attempt_escape(self,keys):
        if self.immunity['left_or_right'] == 'left':
            if keys[K_RIGHT] and not keys[K_LEFT]:
                self.immunity['escape'] += 40 
                self.immunity['left_or_right'] = 'right'
        elif not keys[K_RIGHT] and keys[K_LEFT]:
            self.immunity['escape'] += 40 
            self.immunity['left_or_right'] = 'left'
        if self.immunity['escape'] >= 300:
            self.remove_status('Bind')
            self.immunity['immunity'] = True
            self.immunity['duration'] = 120
            self.immunity['escape'] = 0
