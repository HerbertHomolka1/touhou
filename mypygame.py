import pygame
from pygame.locals import *
import math
import csv
from queue import PriorityQueue
import heapq  

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

def setup_walls(grid):
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


def chest_behaviour(chests,switches):
    for chest in chests:
        chest.try_opening(switches)
        if chest.closed == True:
            pygame.draw.rect(window, PINK, (chest.x, chest.y, chest.size, chest.size))
        else:
            pygame.draw.rect(window, GREEN, (chest.x, chest.y, chest.size, chest.size))

def enemy_behaviour(enemies,you,walls):
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

        angle,distance = get_angle_and_distance(you,enemy)

        if not enemy.name == 'Military Drone': # this must be updated. we assume the mosnter will always go towards you, which might not always be the case

            if enemy.noticed_player:
               
                if len(enemy.path) == 0:
                        
                    enemy.path = enemy.a_star((enemy.x,enemy.y),(you.x,you.y),walls)[1:]
                    enemy.close_on_you(you)
                   
                else:
                    enemy.close_on_you(enemy.path[0])
                    if enemy.rect.colliderect(enemy.path[0][0],enemy.path[0][1],10,10):
                        enemy.path = enemy.path[1:]
                

        else:
            enemy.drone_linger(you)
             
        for enemy in enemies:
            enemy.rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
            enemy.countdown()

            #angle,distance = get_angle_and_distance(you,enemy)
    
            #enemy.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles)    # unaimed shot
            
            if enemy.noticed_player:
                predicted_x, predicted_y = predict_target_position(you.x, you.y, (you.x-you.original_x,you.y-you.original_y),  8)
                
                angle,distance = get_angle_and_distance((predicted_x,predicted_y), enemy)

                enemy.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles) 

        for enemy in enemies:
            avoid_wall_collision(enemy)

        if not you.immunity['immunity']:
            for enemy in enemies:
                if enemy.rect.colliderect(you):
                    
                    you.inflict_status(bind)


def switch_behaviour(switches,you):
    for switch in switches:
        if switch.state == True:
            pygame.draw.rect(window, GREEN, (switch.x, switch.y, switch.size, switch.size))
        else:
            pygame.draw.rect(window, (140,110,23), (switch.x, switch.y, switch.size, switch.size))
        
        if switch.rect.colliderect(you):
            switch.switch()

def area_behaviour(areas, you):
    for area in areas:
        circle_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        circle_color = pygame.Color(71, 136, 0, 100)
        circle_radius = 100
        pygame.draw.circle(circle_surface, circle_color, (100, 100), circle_radius)
        window.blit(circle_surface, (area.x, area.y))
        area.deal_damage(you)

def projectile_behaviour(projectiles,enemies):
    for projectile in projectiles:
        for enemy in enemies:
            if enemy.rect.colliderect(projectile):
                if projectile.owner not in enemies:
                    enemy.hp -= projectile.damage
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                    projectiles.remove(projectile)
        projectile.update()
        projectile.draw()

def bottom_text_render(you,enemies,chests):
    
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
        if calculate_distance((you.x,you.y),(enemy.x+enemy.size/2,enemy.y+enemy.size/2)) < 200:
                who_says = enemy
                break
    if who_says:
        say_sth(who_says,who_says.text)

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

def avoid_wall_collision(who):
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

def predict_target_position(target_x, target_y, target_speed, projectile_speed, iterations=10):
    predicted_x = target_x
    predicted_y = target_y

    for _ in range(iterations):
        distance = calculate_distance((enemy.x, enemy.y), (predicted_x, predicted_y))
        time = distance / projectile_speed
        time /= iterations  # Divide time by the number of iterations
        predicted_x += target_speed[0] * time
        predicted_y += target_speed[1] * time

    return predicted_x, predicted_y

# Function to calculate the distance between two points
def calculate_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Generate a list of neighboring nodes for a given position
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

class Node:
    def __init__(self, position, g_cost, h_cost, parent):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent

    def f_cost(self):
        return self.g_cost + self.h_cost


    def __lt__(self, other):
        return self.f_cost() < other.f_cost()

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
                if not is_valid_position(neighbor, self.size, walls) or neighbor in closed_set:
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
        print("{} attacks for {} damage.".format(self.name, my_damage))
        whom.receive_damage(my_damage)

    def receive_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            print("{} has been defeated!".format(self.name))
        else:
            print("{} received {} damage. Remaining HP: {}".format(self.name, damage, self.hp))

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




    def check_obstacles_in_line(self,player, obstacles):
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

    def teleport(self, keys):
        if 'teleport' in self.learned_spells:
            #say_sth(you,str(self.teleport_countdown))
            if keys[K_SPACE]:

                if self.teleport_countdown == 0:
                    
                    if keys[K_RIGHT]:
                        self.x += 400
                    elif keys[K_LEFT]:
                        self.x -= 400
                    else:
                        self.x += 0
                    if keys[K_DOWN]:
                        self.y += 400
                    elif keys[K_UP]:
                        self.y -=400
                    else:
                        self.y += 0
                        print(keys[K_RIGHT] or keys[K_DOWN])

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
        if you.immunity['duration']>0:
            you.immunity['duration'] -= 1
        if you.immunity['escape']>0:
            you.immunity['escape'] -= 1
        if you.immunity['duration'] ==0:
            you.immunity['immunity'] = False

    def try_shooting(self):
        if event.type == pygame.MOUSEBUTTONUP:
            
            pos = pygame.mouse.get_pos()

            angle,distance = get_angle_and_distance(pos,you)
            if 'Bind' not in you.status:
                you.shoot_projectile(1* math.cos(angle),1* math.sin(angle),projectiles)   



    def control_your_movement(self,keys):

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

        you.teleport(keys)
        

        you.rect = pygame.Rect(you.x, you.y, you.size, you.size)
        avoid_wall_collision(you)

    def attempt_escape(self):
        if you.immunity['left_or_right'] == 'left':
            if keys[K_RIGHT] and not keys[K_LEFT]:
                you.immunity['escape'] += 40 
                you.immunity['left_or_right'] = 'right'
        elif not keys[K_RIGHT] and keys[K_LEFT]:
            you.immunity['escape'] += 40 
            you.immunity['left_or_right'] = 'left'
        if you.immunity['escape'] >= 300:
            you.remove_status('Bind')
            you.immunity['immunity'] = True
            you.immunity['duration'] = 120
            you.immunity['escape'] = 0




class HumanGuard(Character):
    def __init__(self):
        super().__init__(25,"Human Guard", 500, 700, 2, 1, 5, 'You\'re not getting away with this!')

    def close_on_you(self,you):
        self.original_x = self.x
        self.original_y = self.y

        angle,distance = get_angle_and_distance(you,enemy)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        avoid_wall_collision(self)



class BasicMonster(Character):
    def __init__(self):
        super().__init__(70,"Monster of the week", 1200, 600, 1, 5, 100, 'Me da strongest')

    def close_on_you(self,you):
        self.original_x = self.x
        self.original_y = self.y

        angle,distance = get_angle_and_distance(you,enemy)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        avoid_wall_collision(self)  
        
class MilitaryDrone(Character):
    def __init__(self):
        super().__init__(15,"Military Drone", 780, 170, 3, 5, 100, 'target apprehended')

    def drone_linger(self,you):

        self.original_x = self.x
        self.original_y = self.y

        angle,distance = get_angle_and_distance(you,self)
        if distance > drone_distance+30:

            self.x += self.speed * math.cos(angle)
            self.y += self.speed * math.sin(angle)
        elif distance < drone_distance -30:

            self.x -= self.speed * math.cos(angle)
            self.y -= self.speed * math.sin(angle) 
        else:

            # Calculate the angle perpendicular to the drone's position
            perpendicular_angle = angle + math.pi/2

            # Calculate the new x and y coordinates for circular movement
            self.x = self.original_x + self.speed * math.cos(perpendicular_angle)
            self.y = self.original_y + self.speed * math.sin(perpendicular_angle)


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

    def update(self):
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


bind = Bind()

class Switch():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = False
        self.size = 10
    
    def switch(self):
        self.state = True

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


class Level():
    levels = []
    def __init__(self, requirements, lvl,layout):
        self.requirements = requirements
        self.lvl = lvl
        self.layout = layout
    def lvlup(self):
        if self.requirements:
            Level.levels.pop(0)

class Area():
    def __init__(self, x,y,radius,damage):
        self.x =x
        self.y = y
        self.radius = radius
        self.damage = damage
        
    
    def deal_damage(self,to_whom):
        if calculate_distance((to_whom.x + to_whom.size/2 ,to_whom.y+to_whom.size/2),(self.x+self.radius,self.y+self.radius)) < self.radius + to_whom.size/2:
            to_whom.receive_damage(self.damage)


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

# Set up the display
window_width, window_height = 1600, 900
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("MyGame")
font = pygame.font.Font(None, 36)

# Set up the main character
your_size = 25
you = Player()

you.rect = pygame.Rect(you.x,you.y,you.size, you.size)

# Set up the enemy

enemies = []
projectiles = []
drone_distance = 200
    

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
PINK = (255,192,203)

# Set up the walls
wall_thickness = 20


# Create a list to store the walls
walls = []
switches = []
chests = []
areas = []

# Iterate over the grid and create walls based on the CSV contents
# Initialize variables
# Convert CSV data to a list of grid coordinates

grid,grid_coordinates = get_grid_from_csv()

walls = setup_walls(grid)

         


# Game loop
running = True
clock = pygame.time.Clock()

while running:
 

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        you.try_shooting()
 

    # Get the current state of the keyboard
    keys = pygame.key.get_pressed()
    
    # Update the player's position based on the pressed keys

    if 'Bind' in you.status:
        you.attempt_escape()
    else:
        you.control_your_movement(keys)    # Update the enemy's position to move towards the player

    you.immunity_check_and_setup()

    #print(you.stealth)

    enemy_behaviour(enemies, you, walls)

    # Draw the background
    window.fill((255, 255, 255))
    
    # draw the walls
    for wall in walls:
        pygame.draw.rect(window, GRAY, wall)

    # Draw the player
    pygame.draw.rect(window, BLUE, (you.x, you.y, your_size, your_size))

    # Draw the enemy
    for enemy in enemies:
        pygame.draw.rect(window, RED, (enemy.x, enemy.y, enemy.size, enemy.size))
    
    switch_behaviour(switches,you)

    chest_behaviour(chests,switches)

    # area gives you a damage over time, think fire, poison gas etc. the one i set up is for test

    a = Area(600,450,100,1/30)
    areas = []
    areas += [a]

    area_behaviour(areas, you)

    projectile_behaviour(projectiles,enemies) # draw projectile, check if it hits anything etc

    you.countdown() # related to shooting? change name
    
    you.check_for_and_activate_spells(keys)

    bottom_text_render(you,enemies,chests) # render what the enemies are saying

    # Update the display
    pygame.display.update()

    # Control the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()