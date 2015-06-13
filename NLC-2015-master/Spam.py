import pygame
from vector2 import Vector2 as vec2
from StateMachine import *
from ImageFuncs import ImageFuncs
import ani
from math import sin, cos, radians, atan2, degrees
import Shot
import random
from Enemies import RoamPoint, BaseEnemy

debug = False
screen_size = vec2(1000, 600)

class Spam(BaseEnemy):

    def __init__(self,world, pos):
        BaseEnemy.__init__(self, world, pos)
        self.ani = ani.Ani(6, .2)
        self.imagefuncs = ImageFuncs(32,32,world.base_image)
        self.lst = self.imagefuncs.get_images(6,0,3)
        self.max_range = 650
        self.attacking_range = 300
        self.scared_range = 250
        self.reload_max = 2
        self.reload = self.reload_max
        self.fired = False
        self.dead = False

        """AI variables"""
        self.roaming_state = Roaming(self, self.player)
        self.pursuing_state = Pursuing(self, self.player)
        self.attacking_state = Attacking(self, self.player)
        self.idle_state = Idle(self, self.player)

        self.brain.add_state(self.roaming_state)
        self.brain.add_state(self.pursuing_state)
        self.brain.add_state(self.attacking_state)
        self.brain.add_state(self.idle_state)

        self.brain.set_state("idle")

        """Image variables"""

        """Image variables"""
        self.img = self.world.image_funcs.get_image(0, 3)
        self.img.set_colorkey((255, 0, 255))
        self.image = self.img

        self.rect = self.img.get_rect()


class Attacking(State):
    """The enemy can see the player and is actively attacking them them, 
        staying away if possible"""

    def __init__(self, enemy, player):
        State.__init__(self, "attacking")
        self.enemy = enemy
        self.player = player
        self.b_img = pygame.image.load("res/mail.png").convert()

    def do_actions(self, tick):
        self.enemy.reload -= tick
        self.enemy.img = self.enemy.image
        if self.enemy.reload <= 0:
            """fire"""
            self.enemy.img = self.enemy.lst[self.enemy.ani.get_frame(tick)]
            self.enemy.image = self.enemy.img
            self.enemy.img.set_colorkey((255, 0, 255))

            if self.enemy.ani.finished == True:
                self.enemy.ani.finished = False
                dx = self.enemy.pos.x - self.player.pos.x
                dy = self.enemy.pos.y - self.player.pos.y
                for i in xrange(10):
                    a = random.randint(int(dx-60), int(dx+60))
                    b = random.randint(int(dy-60), int(dy+60))
                    angle = atan2(b, a)
                    vel = vec2(cos(angle), sin(angle)) * -350
                    temps = Shot.Shot(self.enemy.pos.copy(), angle, vel)
                    temps.img = self.b_img
                    temps.img.set_colorkey((255, 0, 255))
                    temps.img = pygame.transform.rotate(temps.img, 
                            180 - degrees(temps.angle))
                    temps.rect = temps.img.get_rect()
                    self.enemy.bullet_list.append(temps)

                self.enemy.reload = self.enemy.reload_max
                self.enemy.ani.reset()
                self.fired = True

    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) > self.enemy.scared_range:
            return "pursuing"

        if self.enemy.fired:
            self.enemy.fired = False
            return "pursuing"

    def entry_actions(self):
        self.velocity = vec2()

    def exit_actions(self):
        pass

class Pursuing(State):
    """The enemy can see the player but is not in range to attack"""

    def __init__(self, enemy, player):
        State.__init__(self, "pursuing")
        self.enemy = enemy
        self.player = player

    def do_actions(self, tick):
        """flying towards the player while firing"""

        self.enemy.velocity += self.enemy.get_vector_to_target() * self.enemy.acceleration * tick

        self.enemy.reload -= tick

    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) <= self.enemy.scared_range:
            return "attacking"

        if not self.enemy.can_see(self.player):
            return "roaming"

    def entry_actions(self):
        self.enemy.target = self.player

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

    def do_actions(self, tick):
        self.enemy.velocity += self.enemy.get_vector_to_target() * self.enemy.acceleration * tick

        if self.enemy.get_dist_to(self.enemy.target.pos) < 25:
            angle = radians(random.randint(0, 359))
            self.enemy.target = RoamPoint(self.enemy.pos + vec2(cos(angle), 
                    sin(angle)) * random.randint(50, 250))

    def check_conditions(self):
        if self.enemy.can_see(self.player):
            return "pursuing"

    def entry_actions(self):
        angle = radians(random.randint(0, 359))
        self.enemy.target = RoamPoint(self.enemy.pos + vec2(cos(angle), 
                sin(angle)) * random.randint(25, 150))

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

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
