import pygame, math, Shot

from vector2 import Vector2 as vec2

debug = False
screen_size = vec2(1000, 600)


class Player(object):
    def __init__(self, world, img, pos):
        self.world = world
        
        self.pos = vec2(pos)
        self.image = img
        self.img = img
        self.img.set_colorkey((255, 0, 255))
        
        self.acc_const = 5
        self.bullet_list = self.world.bullet_list
        self.reload_max = .15
        self.reload = self.reload_max

        self.firewall_reload_max = 5
        self.firewall_reload = self.firewall_reload_max

        self.num_fullscan = 1
        self.fullscan_reload_max = 1
        self.fullscan_reload = self.fullscan_reload_max

        self.mxy = vec2(0, 0)
        self.dxy = vec2(0, 0)
        self.rect = self.img.get_rect()
        self.mask = pygame.mask.from_surface(self.img)
        self.speed = 300

        self.health = 100
        self.health_max = self.health
        self.invulnerable = False

        self.velocity = vec2()
        self.acceleration = 5

        self.points = 0

    def vec_to_int(self, vec):
        return int(vec.x), int(vec.y)

    def clamp_vec(self, vec):
        new_vec = vec2()
        new_vec.x = max(0, min(vec.x, screen_size.x))
        new_vec.y = max(0, min(vec.y, screen_size.y))

        return new_vec

    def cap(self, vec, lower, upper):
        """caps a vector to a certain threshold"""
        new_vec = vec2()
        new_vec.x = max(lower, min(vec.x, upper))
        new_vec.y = max(lower, min(vec.y, upper))

        return new_vec

    def get_angle(self, pos):
            dy = pos.y-self.rect.center[1]
            dx = pos.x-self.rect.center[0]
            angle = math.atan2(dy, dx)
            return angle

    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.img = rot_image
        self.rect = self.img.get_rect()
        self.mask = pygame.mask.from_surface(self.img)

    def shoot(self, pos):
        if self.reload <= 0:
            self.world.sound_classes[2].play()

            angle = self.get_angle(pos)
            vel = vec2(math.cos(angle), math.sin(angle)) * 500

            x = self.pos.copy()[0]+(math.cos(angle)*20)
            y = self.pos.copy()[1]+(math.sin(angle)*20)

            self.world.instantiate_projectile((x,y), angle, vel, False, True)
            self.velocity -= vel * .0003
            self.reload = self.reload_max

    def firewall(self, pos):
        if self.firewall_reload <= 0:
            
            num_shots = 10
            for i in xrange(num_shots):
                angle = self.get_angle(pos) + math.radians(((num_shots / 2) - i) * (60.0 / num_shots))
                vel = vec2(math.cos(angle), math.sin(angle)) * 500

                x = self.pos.copy()[0] + (math.cos(angle) * 20)
                y = self.pos.copy()[1] + (math.sin(angle) * 20)

                self.world.instantiate_projectile((x, y), angle, vel, False, True, True)
                self.velocity -= vel * .0005
            
            self.firewall_reload = self.firewall_reload_max

    def fullscan(self, pos):
        if self.num_fullscan > 0 and self.fullscan_reload <= 0:

            num_shots = 500
            for i in xrange(num_shots):
                angle = math.radians(((num_shots / 2) - i) * 360.0 / num_shots)
                vel = vec2(math.cos(angle), math.sin(angle)) * 500

                x = self.pos.copy()[0] + (math.cos(angle) * 20)
                y = self.pos.copy()[1] + (math.sin(angle) * 20)

                self.world.instantiate_projectile((x, y), angle, vel, False, True, False)

            self.num_fullscan -= 1
            self.fullscan_reload = self.fullscan_reload_max

    def move(self):
        self.pos.set_x(self.pos.get_x()+self.dxy.get_x())
        self.pos.set_y(self.pos.get_y()+self.dxy.get_y())

    def update(self, pos, movement, tick):
        self.reload -= tick
        self.firewall_reload -= tick
        self.fullscan_reload -= tick

        self.velocity *= .99
        self.velocity += movement.normalise() * self.acceleration * tick
        capped_vel = self.cap(self.velocity, -10, 10)

        self.pos += capped_vel

        self.rot_center(-math.degrees(self.get_angle(pos))-90)

    def render(self, surface, camera):
        self.rect.center = self.pos + camera.offset
        surface.blit(self.img, self.rect)
