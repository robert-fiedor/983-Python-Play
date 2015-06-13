import pygame
from math import degrees


class Shot(object):

    def __init__(self, pos, angle, vel, bool_enemy=True, bool_player=False, bool_fire=False):
        self.pos = pos
        self.vel = vel
        self.angle = angle
        self.bool_enemy = bool_enemy

        self.life = 2
        self.dead = False        

        if bool_fire:
            self.img = pygame.image.load("res/fire.png").convert()
        elif bool_player:
            self.img = pygame.image.load("res/disc.png").convert()
        else:
            self.img = pygame.image.load("res/bullet.png").convert()
        self.img.set_colorkey((255, 0, 255))
        self.img = pygame.transform.rotate(self.img, 180-degrees(self.angle))
        self.rect = self.img.get_rect()

    def update(self, tick):
        self.life -= tick
        if self.life <= 0:
            self.dead = True

        self.pos += self.vel * tick
        self.rect.center = self.pos

    def check_collisions(self, ent):
        if ent.rect.colliderect(self.rect):
            return True

        return False

    def get_mask(self):
        self.mask = pygame.mask.from_surface(self.img)

    def render(self, surface, camera):
        self.rect.center = self.pos + camera.offset
        surface.blit(self.img, self.rect)
