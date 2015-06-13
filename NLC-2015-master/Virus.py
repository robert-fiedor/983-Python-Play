import pygame
from vector2 import Vector2 as vec2
from StateMachine import *
from ImageFuncs import ImageFuncs
import Shot
from math import radians, sin, cos
import random
from Enemies import BaseEnemy, RoamPoint, Roaming

debug = False
screen_size = vec2(1000, 600)


class Virus(BaseEnemy):

    def __init__(self, world, pos):
        BaseEnemy.__init__(self, world, pos)
        
        """Base variables"""
        self.max_range = 650
        self.attacking_range = 350
        self.scared_range = 0
        self.ranged = False
        self.dead = False
        self.damage_dealt_on_death = 5

        self.reload_max = 0
        self.food = 0

        """AI variables"""
        self.reproducing_state = Reproducing(self, self.player)
        self.roaming_state = Roaming(self, self.player)
        self.attacking_state = Attacking(self, self.player)
        self.idle_state = Idle(self, self.player)

        self.brain.add_state(self.reproducing_state)
        self.brain.add_state(self.roaming_state)
        self.brain.add_state(self.attacking_state)
        self.brain.add_state(self.idle_state)

        self.brain.set_state("idle")
        
        """Image variables"""
        self.image = self.world.image_funcs.get_image(random.randint(0,1), 1)
        self.image.set_colorkey((255, 0, 255))
        self.img = self.image
        self.rect = self.img.get_rect()
        self.nodam = False
        self.damcount = 0

        self.max_ents = 0

        
class Reproducing(State):

    def __init__(self, enemy, player):
        State.__init__(self, "reproducing")
        self.enemy = enemy
        self.player = player

    def entry_actions(self):
        pass

    def do_actions(self, tick):
        v_lst = []
        self.enemy.food += tick
        for i in self.enemy.world.enemy_list:
            try:
                if i.max_virus == self.enemy.max_virus:
                    v_lst.append(i)
            except Exception:
                pass
        if self.enemy.food > 3.14159 and len(v_lst) < self.enemy.max_virus:
            new_virus = Virus(self.enemy.world, self.enemy.pos.copy()+vec2(random.random(), random.random()))
            self.enemy.food = 0
            self.enemy.world.enemy_list.append(new_virus)

    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) < self.enemy.attacking_range:
            return "attacking"

        if self.enemy.food == 0 and random.randint(0,1)or len(self.enemy.world.enemy_list) >= self.enemy.max_ents:
            return "roaming"

    def exit_actions(self):
        self.enemy.food = 0


class Attacking(State):

    def __init__(self, enemy, player):
        State.__init__(self, "attacking")
        self.enemy = enemy
        self.player = player

    def entry_actions(self):
        self.enemy.target = self.player

    def do_actions(self, tick):
        if self.enemy.nodam == True:
            self.enemy.damcount += tick
            if self.enemy.damcount >= 2:
                self.enemy.nodam = False
        self.enemy.velocity += self.enemy.get_vector_to_target() * self.enemy.acceleration * tick
        if self.enemy.get_dist_to(self.player.pos) < self.enemy.radius:
            """Explode"""
            if self.enemy.nodam == False:
                self.player.health -= self.enemy.damage_dealt_on_death
            self.enemy.nodam = True
            self.player.velocity += self.enemy.velocity
            self.enemy.velocity = self.enemy.velocity.normalize()*-5


    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) > self.enemy.max_range:
            return "roaming"

    def exit_actions(self):
        pass

class Roaming(State):
    """ If you don't want the AI to just sit idle, this makes it aimlessly roam
        around when it can't see the player, because of the way movement works
        with acceleration it looks like a hive when there are a lot of them"""

    def __init__(self, enemy, player):
        State.__init__(self, "roaming")
        self.enemy = enemy
        self.player = player
        self.there = False

    def do_actions(self, tick):
        self.enemy.velocity += self.enemy.get_vector_to_target() * self.enemy.acceleration * tick
        self.there = False
        
        if self.enemy.get_dist_to(self.enemy.target.pos) < 25:
            angle = radians(random.randint(0, 359))
            self.enemy.target = RoamPoint(self.enemy.pos+vec2(cos(angle), sin(angle))*random.randint(50, 250))
            self.there = True
            
    def check_conditions(self):
        if self.enemy.can_see(self.player):
            return "attacking"

        elif self.there and random.randint(0,1) and len(self.enemy.world.enemy_list) < self.enemy.max_ents:
            return "reproducing"

        if self.enemy.get_dist_to(self.player.pos) >= 700:
            return "idle"

    def entry_actions(self):
        angle = radians(random.randint(0, 359))
        self.enemy.target = RoamPoint(self.enemy.pos+vec2( cos(angle),sin(angle))*random.randint(25, 150))

    def exit_actions(self):
        pass


class Idle(State):
    """The player is too far away and we want to stay in a low memory usage state"""

    def __init__(self, enemy, player):
        State.__init__(self, "idle")
        self.enemy = enemy
        self.player = player

    def do_actions(self, tick):
        pass

    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) < 700:
            return "roaming"

        elif random.randint(0, 10):
            return "reproducing"

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
