import pygame
from vector2 import Vector2 as vec2
import random
debug = False
import random

class WorldMap(object):

    def __init__(self, world, size, each_size):
        self.map_filename = world.map_filename
        self.map_images = world.marching_images
        self.map_array = [[self.Tile((j, i), each_size, self.map_images) for i in xrange(size[0])] for j in xrange(size[1])]
        self.map_file = open(self.map_filename, "r")

        self.map_render = None
        self.map_mask = None

        y = 0
        for line in self.map_file.readlines():
            x = 0
            for character in line:
                try:
                    self.map_array[x][y].on = bool(int(character))
                except ValueError:
                    """This is to handler the /n at the end of the lines"""
                    pass
                x += 1
            y += 1

        self.map_file.close()

        self.w, self.h = x, y
        self.each_size = each_size

    def update(self):
        for tile_list in self.map_array:
            for tile in tile_list:
                tile.update(self.map_array)

    def test_collisions_point(self, pos):
        updated_pos = (int(pos[0]), int(pos[1]))
        for tile_list in self.map_array:
            for tile in tile_list:
                try:
                    if tile.test_collision_point(updated_pos):
                        return True
                except IndexError:
                    continue

        return False

    def render(self, surface, camera):
        if self.map_render is None:
            self.map_render = pygame.Surface((self.w * self.each_size, self.h * self.each_size))
            for tile_list in self.map_array:
                for tile in tile_list:

                    tile.render(self.map_render)

        surface.blit(self.map_render, camera.offset)


    class Tile:

        def __init__(self, pos, tile_size, total_images):
            self.tl = 8
            self.tr = 4
            self.br = 2
            self.bl = 1
            self.on = False
            self.pos = pos
            self.grand_size = tile_size
            self.total_images = total_images
            self.mask = None
            self.img = None

        def update(self, data_map):
            total = 0
            size = self.grand_size
            x, y = self.pos
            if data_map[x][y].on:
                total += self.tl
            if data_map[(x+1) % len(data_map)][y].on:
                total += self.tr
            if data_map[(x+1) % len(data_map)][(y+1) % len(data_map[0])].on:
                total += self.br
            if data_map[x][(y+1) % len(data_map[0])].on:
                total += self.bl

            new_y = total // 4
            new_x = total % 4

            a = random.randint(0,len(self.total_images)-1)
            self.img = pygame.transform.scale(self.total_images[a].subsurface(new_x*32, new_y*32, 32, 32), (size, size))
            self.mask = pygame.mask.from_surface(self.img)
            self.rect = self.img.get_rect()

        def test_collision_point(self, point):
            offset = (  int(point[0]) - (self.pos[0]) * self.grand_size,
                        int(point[1]) - (self.pos[1]) * self.grand_size)
            offset2 = [offset[0]/self.grand_size, offset[1]/self.grand_size]
            
            return self.mask.get_at(offset)

        def render(self, surface):
            surface.blit(self.img, (self.pos[0]*self.grand_size,
                                    self.pos[1]*self.grand_size))

            if debug:
                x, y = (self.pos[0]*self.grand_size,
                        self.pos[1]*self.grand_size)
                pygame.draw.rect(surface,(255,0,0),((x,y),(self.grand_size,self.grand_size)),1)
