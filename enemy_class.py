from character_class import Character
import math

class HumanGuard(Character):
    def __init__(self):
        super().__init__(25,"Human Guard", 500, 700, 2, 1, 5, 'You\'re not getting away with this!')

    def close_on_you(self,you):
        self.original_x = self.x
        self.original_y = self.y

        angle, _ = Game.get_angle_and_distance(you,enemy)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        Character.avoid_wall_collision(self)



class BasicMonster(Character):
    def __init__(self):
        super().__init__(70,"Monster of the week", 1200, 600, 1, 5, 100, 'Me da strongest')

    def close_on_you(self,you,walls):
        from game_class import Game
        self.original_x = self.x
        self.original_y = self.y

        angle, _ = Game.get_angle_and_distance(you,self)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        Character.avoid_wall_collision(self,walls)  
        
class MilitaryDrone(Character):
    def __init__(self):
        super().__init__(15,"Military Drone", 780, 170, 3, 5, 100, 'target apprehended')

    def drone_linger(self,you):

        self.original_x = self.x
        self.original_y = self.y

        angle,distance = Game.get_angle_and_distance(you,self)
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

