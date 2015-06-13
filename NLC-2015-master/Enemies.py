import pygame
from vector2 import Vector2 as vec2
from StateMachine import *
from ImageFuncs import ImageFuncs
from math import sin, cos, radians, atan2, degrees, pi
import Shot
import random
import math

debug = False
screen_size = vec2(1000, 600)


class BaseEnemy(object):

    def __init__(self, world, pos):
        """Base variables"""
        self.world = world
        self.pos = pos
        self.player = self.world.player

        self.acceleration = 5
        self.max_range = 300
        self.attacking_range = 150
        self.scared_range = 100
        self.bullet_list = self.world.bullet_list
        self.invulnerable = False

        self.reload_max = 5
        self.reload = self.reload_max

        self.velocity = vec2()

        self.target = self.player

        self.mask = None
        self.look_ahead = 50
        self.health = 50
        self.health_max = self.health

        """AI variables"""
        self.brain = StateMachine()

        self.radius = 25
            
        self.hit_this_frame = False
        self.visible = True

    def update(self, tick):
        """ called every frame, the tick is the time passed since the last frame.
            Multiplying movement by it causes movement to be the same speed
            regardless of how fast a computer is (not good when frame rate is low)"""
        self.brain.think(tick)

        self.velocity *= 0.99
        capped_vel = vec2()
        if self.velocity.x < -10:
            capped_vel.x = -10
        elif self.velocity.x > 10:
            capped_vel.x = 10
        else:
            capped_vel.x = self.velocity.x

        if self.velocity.y < -10:
            capped_vel.y = -10
        elif self.velocity.y > 10:
            capped_vel.y = 10
        else:
            capped_vel.y = self.velocity.y
        #capped_vel = self.cap(self.velocity, -10, 10)

        self.pos += capped_vel
        self.rect.center = self.pos
        self.mask = pygame.mask.from_surface(self.img)
        """
        if self.world.main_map.test_collisions_point(self.pos):
            self.velocity*=-.5
        """

    def update_collisions(self, enemy_list):
        if self.__class__.__name__ == "Boss":
            return
        for i, current_enemy in enumerate(enemy_list):
            if current_enemy is self or current_enemy.__class__.__name__ == "Boss":
                continue
            current_vec = vec2().from_points(self.pos, current_enemy.pos)
            if current_vec.get_magnitude() < self.radius + current_enemy.radius:
                self.pos -= 0.1 * current_vec
                current_enemy.pos += 0.1 * current_vec

        self.rect.center = self.pos
        current_enemy.rect.center = current_enemy.pos

    def get_angle_to_target(self):
            dy = self.target.pos[1]-self.rect.center[1]
            dx = self.target.pos[0]-self.rect.center[0]
            angle = atan2(dy, dx)
            return angle

    def change_target(self):
        angle = random.uniform(0, 2*pi)
        self.target = RoamPoint(self.pos + vec2(cos(angle), sin(angle)) * random.randint(50, 250))

    def health_bar(self, screen):
        if self.visible == True:
            width = int((self.img.get_width()/2)*(self.health/float(self.health_max)))
            pos = (self.rect.center[0]-(self.img.get_width()/2),self.rect.center[1]+(self.img.get_height()/2)+5)
            w,h = (self.img.get_width(),5)
            pygame.draw.rect(screen,(255,0,0),((pos),(w,h)),0)
            pygame.draw.rect(screen,(0,255,0),((pos),(w*(self.health/float(self.health_max)),h)),0)

    def rot_center(self):
        angle = self.get_angle_to_target()
        angle = 180-degrees(angle)
        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.img = rot_image
        self.rect = self.img.get_rect()
        self.mask = pygame.mask.from_surface(self.img)

    def get_vector_to_target(self):
        """returns the normalized vector between the enemy and target"""
        if self.target is None:
            return vec2()

        return vec2(self.target.pos - self.pos).normalise()

    def cap(self, vec, lower, upper):
        """caps a vector to a certain threshold"""
        new_vec = vec2()
        new_vec.x = max(lower, min(vec.x, upper))
        new_vec.y = max(lower, min(vec.y, upper))

        return new_vec

    def get_dist_to(self, other_vec):
        return vec2(other_vec - self.pos).get_magnitude()

    def can_see(self, player):
        """tests to see if the enemy can see the player"""
        if self.get_dist_to(player.pos) > self.max_range:
            return False

        return True

    def vec_to_int(self, vec):
        return int(vec.x), int(vec.y)

    def render(self, surface, camera):
        """renders the enemy to the given surface"""

        self.rect.center = self.pos + camera.offset
        surface.blit(self.img, self.rect)
        self.health_bar(surface)


class RoamPoint(object):

    def __init__(self, pos):
        self.pos = pos


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
            return "pursuing"

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

    def do_actions(self, tick):
        """backing away while firing"""

        self.enemy.velocity -= self.enemy.get_vector_to_target() * self.enemy.acceleration * tick
        self.enemy.reload -= tick
        if self.enemy.reload <= 0:
            """fire"""
            dx = self.enemy.pos.x - self.player.pos.x
            dy = self.enemy.pos.y - self.player.pos.y
            angle = atan2(dy, dx)
            vel = vec2(cos(angle), sin(angle))*-250

            x = self.enemy.copy()[0]+(math.cos(angle)*20)
            y = self.enemy.copy()[1]+(math.sin(angle)*20)

            self.enemy.bullet_list.append(Shot.Shot(self.enemy.pos.copy(), angle, vel))
            self.enemy.reload = self.enemy.reload_max



    def check_conditions(self):
        if self.enemy.get_dist_to(self.player.pos) > self.enemy.scared_range:
            return "pursuing"

    def entry_actions(self):
        pass

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
        if self.enemy.reload <= 0 and self.enemy.get_dist_to(self.player.pos) < self.enemy.attacking_range and self.enemy.attacking_range!=0:
            """fire"""
            dx = self.enemy.pos.x - self.player.pos.x
            dy = self.enemy.pos.y - self.player.pos.y
            angle = atan2(dy, dx)
            vel = vec2(cos(angle), sin(angle))*-250
            self.enemy.bullet_list.append(Shot.Shot(self.enemy.pos.copy(), angle, vel))
            self.enemy.reload = self.enemy.reload_max


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
            while self.enemy.world.main_map.test_collisions_point(self.enemy.target.pos):
            
                angle = radians(random.randint(0, 359))
                self.enemy.target = RoamPoint(self.enemy.pos+vec2(cos(angle), sin(angle))*random.randint(50, 250))
    def check_conditions(self):
        if self.enemy.can_see(self.player):
            return "pursuing"

    def entry_actions(self):
        print "I AM ROAMING"
        while self.enemy.world.main_map.test_collisions_point(self.enemy.target.pos):
            angle = radians(random.randint(0, 359))
            self.enemy.target = RoamPoint(self.enemy.pos+vec2( cos(angle),sin(angle))*random.randint(25, 150))

    def exit_actions(self):
        pass
