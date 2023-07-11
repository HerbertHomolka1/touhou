import pygame
from node_class import Node
from projectile_class import Projectile
import heapq
import math


class Character:
    def __init__(self, size,name, x, y, speed, strength, hp, text,equipped_items={}):
        self.size = size
        self.name = name
        self.x = x 
        self.y = y
        self.immunity = {'immunity':False,'duration':0,'escape':0,'left_or_right':'left'}
        self.path = []
        self.check_time = 120
        self.original_x = x
        self.original_y = y
        self.speed = speed
        
        self.strength = strength
        self.hp = hp
        self.status = dict()
        self.equipped_items = dict()

        self.shot_cooldown_time = 60 # later will have to be moved into the paricular weapon you use, eg bow, gun, etc
        self.shot_countdown = 0
        self.path = []
        self.noticed_player = False
        self.text = text
    

    def a_star(self, start, finish, walls):
        open_list = []
        closed_set = set()

        start_node = Node(start, 0, self.get_heuristic(start, finish), None)
        heapq.heappush(open_list, (start_node.f_cost(), start_node))

        while open_list:
            current_node = heapq.heappop(open_list)[1]

            if current_node.position[0] > finish[0] - 60 and current_node.position[0] < finish[0] + 60 and \
                    current_node.position[1] > finish[1] - 60 and current_node.position[1] < finish[1] + 60:
                # Reconstruct the path
                path = []
                while current_node:
                    path.append(current_node.position)
                    current_node = current_node.parent
                path.reverse()
                return path

            closed_set.add(current_node.position)

            neighbors = self.get_neighbors(current_node.position)
            for neighbor in neighbors:
                if not Character.is_valid_position(neighbor, self.size, walls) or neighbor in closed_set:
                    continue

                g_cost = current_node.g_cost + self.get_distance(current_node.position, neighbor)
                h_cost = self.get_heuristic(neighbor, finish)
                neighbor_node = Node(neighbor, g_cost, h_cost, current_node)

                if self.is_node_in_open_list(neighbor_node, open_list):
                    continue

                heapq.heappush(open_list, (neighbor_node.f_cost(), neighbor_node))

        return []  # No valid path found

    def is_node_in_open_list(self, node, open_list):
        for _, open_node in open_list:
            if open_node.position == node.position:
                return True
        return False

    def get_distance(self, position1, position2):
        return ((position2[0] - position1[0]) ** 2 + (position2[1] - position1[1]) ** 2) ** 0.5

    def get_heuristic(self, position, finish):
        return self.get_distance(position, finish)

    def get_neighbors(self, position):
        x, y = position
        neighbors = [
            (x - self.size, y),
            (x + self.size, y),
            (x, y - self.size),
            (x, y + self.size),
        ]  # Left, Right, Up, Down
        return neighbors


    def equip(self, item):
        self.equipped_items[item.__class__.__name__] = item

    def unequip(self, item_name):
        if item_name in self.equipped_items:
            del self.equipped_items[item_name]

    def get_stats(self, stat_as_a_string):
        base_stat = getattr(self, stat_as_a_string)
        equipped_bonus = sum(
            [x.bonus[stat_as_a_string] for x in self.equipped_items.values() if stat_as_a_string in x.bonus]
        )
        status_bonus = sum(
            [x.bonus[stat_as_a_string] for x in self.status.values() if stat_as_a_string in x.bonus]
        )
        the_stat = base_stat + equipped_bonus + status_bonus
        return the_stat if the_stat >= 0 else 0

    def attack(self, whom):
        my_damage = self.get_stats('strength')
     
        whom.receive_damage(my_damage)

    def receive_damage(self, damage):
        self.hp -= damage


    def inflict_status(self, status_effect):
        self.status[status_effect.__class__.__name__] = status_effect

    def remove_status(self, status_name):
        if status_name in self.status:
            del self.status[status_name]


    def shoot_projectile(self, direction_x, direction_y,projectiles):   #self, x, y, direction_x, direction_y, speed
        if self.shot_countdown == 0:
            projectile = Projectile(self.x,self.y,direction_x,direction_y,8,self)
            projectiles.append(projectile)
            self.shot_countdown = self.shot_cooldown_time

    def countdown(self):
        if self.shot_countdown > 0:
            self.shot_countdown -= 1




    def check_obstacles_in_line(self,player, walls):
        if self.noticed_player == False:
            # Calculate the slope between the enemy and player
            dx = player.x - self.x
            dy = player.y - self.y

            # Calculate the step size for x and y coordinates
            if abs(dx) > abs(dy):
                step = abs(dx)
                x_step = 1 if dx > 0 else -1
                y_step = dy / step
            else:
                step = abs(dy)
                y_step = 1 if dy > 0 else -1
                x_step = dx / step

            # Check for obstacles in the line
            for i in range(int(step)):
                x = self.x + i * x_step
                y = self.y + i * y_step

                # Check if the current coordinates contain an obstacle
                temp = pygame.Rect(x,y,20,20)
                for wall in walls:

                    if temp.colliderect(wall):
                        return False
            

            # No obstacles found
            return True
        else:
            return True

    def predict_target_position(self,target_x, target_y, target_speed, projectile_speed, iterations=10):
        from game_class import Game
        
        predicted_x = target_x
        predicted_y = target_y

        for _ in range(iterations):
            distance = Game.calculate_distance((self.x, self.y), (predicted_x, predicted_y))
            time = distance / projectile_speed
            time /= iterations  # Divide time by the number of iterations
            predicted_x += target_speed[0] * time
            predicted_y += target_speed[1] * time

        return predicted_x, predicted_y



    @staticmethod
    def enemy_behaviour(enemies,you,walls,projectiles):
        from game_class import Game
        if not you.stealth: # you = Player()

            for enemy in enemies:
                if enemy.check_time == 0: 
                    enemy.noticed_player = enemy.check_obstacles_in_line(you,walls)
                    enemy.check_time = 120
                else:
                    enemy.check_time -= 1

        for enemy in enemies:
            enemy.original_x = enemy.x
            enemy.original_y = enemy.y

            angle, _ = Game.get_angle_and_distance(you,enemy)

            if not enemy.name == 'Military Drone': # this must be updated. we assume the mosnter will always go towards you, which might not always be the case

                if enemy.noticed_player:
                
                    if len(enemy.path) == 0:
                            
                        enemy.path = enemy.a_star((enemy.x,enemy.y),(you.x,you.y),walls)[1:]
                        enemy.close_on_you(you,walls)
                    
                    else:
                        enemy.close_on_you(enemy.path[0],walls)
                        if enemy.rect.colliderect(enemy.path[0][0],enemy.path[0][1],10,10):
                            enemy.path = enemy.path[1:]
                    

            else:
                enemy.drone_linger(you)
                
            for enemy in enemies:
                enemy.rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                enemy.countdown()

                #angle,distance = Game.get_angle_and_distance(you,enemy)
        
                #enemy.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles)    # unaimed shot
                
                if enemy.noticed_player:
                    predicted_x, predicted_y = enemy.predict_target_position(you.x, you.y, (you.x-you.original_x,you.y-you.original_y),  8)
                    
                    angle,distance = Game.get_angle_and_distance((predicted_x,predicted_y), enemy)

                    enemy.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles) 

            for enemy in enemies:
                Character.avoid_wall_collision(enemy,walls)

            if not you.immunity['immunity']:
                for enemy in enemies:
                    if enemy.rect.colliderect(you):
                        
                        you.inflict_status(bind)




    @staticmethod
    def avoid_wall_collision(who,walls):
        collision = False
        this_wall = 0
        for wall in walls:
            if who.rect.colliderect(wall):
                collision = True
                this_wall = wall
                break

        if collision:
            whox = pygame.Rect(who.original_x,who.y,who.size,who.size)
            whoy = pygame.Rect(who.x,who.original_y,who.size,who.size)

            if not wall.colliderect(whox):

                if [wall.colliderect(whox) for wall in walls].count(True) == 0:
                    # change_x = who.x - who.original_x
                    # change_y = who.y - who.original_y
                    
                    # if abs(change_x) > 50: # case: you teleported. 50 is a random big number here... 
                    #     who.x += 15
                    # elif abs(change_y) > 50:
                    #     who.y += 15
                    
                    # else:  # case: you did not teleport
                    who.x = who.original_x # if you.x + you.speed doesnt cause collision, we can only move in y axis
                else:
                    who.x = who.original_x
                    who.y = who.original_y

            elif not wall.colliderect(whoy):
                if [wall.colliderect(whoy) for wall in walls].count(True) == 0:
                    who.y = who.original_y # if you.x + you.speed doesnt cause collision, we can only move in y axis
                else:
                    who.x = who.original_x
                    who.y = who.original_y
                
            else:
                who.x = who.original_x
                who.y = who.original_y

        who.rect = pygame.Rect(who.x, who.y, who.size, who.size)

    @staticmethod
    def is_valid_position(position, size, walls):
        temp_rect = pygame.Rect(position[0],position[1],size,size)
        for wall in walls:
            if wall.colliderect(temp_rect):
                return False
            if (
                position[0] < 0 or position[0] > 1600 or
                position[1] < 0 or position[1] > 900
            ):
                return False
        return True
