import pygame
from vector2 import Vector2 as vec2
from StateMachine import *
from ImageFuncs import ImageFuncs
import Shot
from math import radians, sin, cos,atan2
import random
from Enemies import BaseEnemy, RoamPoint, Roaming
from Spam import *
from Virus import *
from ani import Ani

debug = False
screen_size = vec2(1000, 600)


class Boss(BaseEnemy):

    def __init__(self, world, pos):
        BaseEnemy.__init__(self, world, pos)

        self.max_range = 500
        self.attacking_range = 500
        self.scared_range = 0
        self.ranged = True
        self.dead = False
        self.health = 1000
        self.health_max = self.health
        self.base_health = self.health
        self.reload_max = 4
        self.reload = self.reload_max
        self.animate = False

        """AI variables"""
        self.attacking_state = Attacking(self, self.player)
        self.idle_state = Idle(self, self.player)

        self.brain.add_state(self.attacking_state)
        self.brain.add_state(self.idle_state)

        self.brain.set_state("idle")

        self.lst = []
        self.lst2 = []

        """Image variables"""
        self.ani = Ani(12,.1)


        a = 0
        b = 0
        for i in range(3):
            for g in range(4):
                self.lst.append(self.world.image_funcs.get_irregular_image(5,5,b,a+5))
                b+=5
            a += 5
            b = 0

        self.img = self.lst[0]
        self.img.set_colorkey((255, 0, 255))
        self.image = self.img

        self.rect = self.img.get_rect()
    def update_collisions(self, enemy_list):
        pass


class Idle(State):
    """When the enemy cannot see the enemy, and does nothing"""

    def __init__(self, enemy, player):
        State.__init__(self, "idle")
        self.enemy = enemy
        self.player = player

    def do_actions(self, tick):
        pass

    def check_conditions(self):
        if self.enemy.can_see(self.player):
            return "attacking"

    def entry_actions(self):
        self.enemy.target = None

    def exit_actions(self):
        pass


class Attacking(State):
    """The enemy can see the player and is actively attacking them them, staying away if possible"""

    def __init__(self, enemy, player):
        State.__init__(self, "attacking")
        self.enemy = enemy
        self.player = player
        self.enemy.world.render_boss = True

    def do_actions(self, tick):
        if self.enemy.dead == True:
            self.enemy.world.game_win = True

        self.enemy.reload -= tick

        if self.enemy.reload <= 0:
            """fire"""
            dx = self.enemy.pos.x - self.player.pos.x
            dy = self.enemy.pos.y - self.player.pos.y
            for i in xrange(25):
                    angle = random.randint(0,360)
                    vel = vec2(cos(angle), sin(angle))*-300
                    self.enemy.bullet_list.append(Shot.Shot(self.enemy.pos.copy(), angle, vel))
            self.enemy.reload = self.enemy.reload_max
        if self.enemy.animate == False:
            if random.randint(0,int((1/tick)*1))==0:
                self.enemy.animate = True
        else:
            self.enemy.img = self.enemy.lst[self.enemy.ani.get_full_frame(tick)]
            self.enemy.img.set_colorkey((255,0,255))
            if self.enemy.ani.run == 1:
                for i in range(2):
                    angle = radians(random.randint(0,359))
                    dist = random.randint(40, 100)
                    vec = self.enemy.pos.copy() + vec2(cos(angle) * dist, sin(angle) * dist)
                    if random.randint(0, 1):
                        self.enemy.world.enemy_list.append(Spam(self.enemy.world, vec))
                    else:
                        self.enemy.world.enemy_list.append(Virus(self.enemy.world, vec))
            if self.enemy.ani.finished == True:
                self.enemy.ani.reset()
                self.enemy.animate = False

