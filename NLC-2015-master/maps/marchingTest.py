import pygame
from pygame.locals import *
pygame.init()

import sys


def main():
    w = h = 512
    screen = pygame.display.set_mode((w, h))

    marchingImg = pygame.image.load("tilemap1.png").convert()

    grandSize = 32

    pygame.font.init()
    font1 = pygame.font.Font(None, 25)

    class tile:

        def __init__(self, pos):
            self.tl = 8
            self.tr = 4
            self.br = 2
            self.bl = 1
            self.on = False
            self.pos = pos

        def update(self, data_map):
            total = 0
            size = grandSize
            x,y = self.pos
            if data_map[x][y].on:
                total += self.tl
            if data_map[(x+1) % len(data_map)][y].on:
                total += self.tr
            if data_map[(x+1) % len(data_map)][(y+1) % len(data_map[0])].on:
                total += self.br
            if data_map[x][(y+1) % len(data_map[0])].on:
                total += self.bl
            newY = total//4
            newX = total%4

            self.image = marchingImg.subsurface(newX*32, newY*32, 32, 32)
            self.img = pygame.transform.scale(self.image, (size, size))

        def render(self, surface):
            surface.blit(self.img, (self.pos[0]*grandSize,self.pos[1]*grandSize))


    class Enemy_text(object):

        def __init__(self, letter, pos):
            self.letter = letter
            self.pos = pos

        def render(self, surface):
            self.img = font1.render(self.letter, True, (255, 0, 0))
            surface.blit(self.img, (self.pos[0] * grandSize, self.pos[1] * grandSize))

        def to_text(self):
            return self.letter + " " + str(self.pos[0]) + " " + str(self.pos[1])


    tileMap = [[tile((x,y)) for y in range(512/grandSize)] for x in range(512/grandSize)]

    for y in range(len(tileMap)):
        for x in range(len(tileMap[0])):
            tileMap[x][y].on = True

    bool_enemy = False

    options = ["map", "enemies", "start", "goal"] 
    option_index = 0

    current_state = options[option_index]

    save_map_name = sys.argv[1]

    start_pos = (1, 1)
    goal_pos = (0, 0)

    enemy_lst = []
    lst = []
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                
                if event.key == K_F2:
                    pygame.image.save(screen, "SCREENSHOT.png")

                if event.key == K_F3:
                    for y in range(len(tileMap)):
                        lst.append([])
                        for x in range(len(tileMap[y])):
                            if tileMap[x][y].on == True:
                                lst[y].append(1)
                            else:
                                lst[y].append(0)
                        lst[y].append(1)
                    
                    with open(save_map_name+".txt", "w") as f :
                        for i in lst:
                            for g in i:
                                g = str(g)
                                a = g.replace("[","")
                                b = a.replace("]","")
                                c = b.replace(",","")
                                f.write(str(c))
                            f.write("\n")

                    f.close()

                    with open(save_map_name+"-enemymap.txt", "w") as f:
                        for e in enemy_lst:
                            f.write(e.to_text() + "\n")
                    f.close()

                    with open(save_map_name+"-startgoals.txt", "w") as f:
                        f.write(str(start_pos[0]) + " " + str(start_pos[1]) + "\n")
                        f.write(str(goal_pos[0]) + " " + str(goal_pos[1]) + "\n")
                    f.close()

                if event.key == K_SPACE:
                    option_index += 1
                    option_index %= len(options)
                    current_state = options[option_index]

            if event.type == MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
                if current_state == "enemies":
                    posX, posY = pygame.mouse.get_pos()
                    posX2 = posX / float(grandSize)
                    posY2 = posY / float(grandSize)
                    
                    pressed_keys = pygame.key.get_pressed()
                    for k in range(len(pressed_keys)):
                        if pressed_keys[k]:
                            enemy_char = pygame.key.name(k)
                            break

                    if event.button == 1:
                        character = enemy_char

                    enemy_lst.append(Enemy_text(character, (posX2, posY2)))

                elif current_state == "start" or current_state == "goal":
                    posX, posY = pygame.mouse.get_pos()
                    posX2 = posX / float(grandSize)
                    posY2 = posY / float(grandSize)
                    
                    if current_state == "start":
                        start_pos = (posX2, posY2)
                    else:
                        goal_pos = (posX2, posY2)

        pressed = pygame.mouse.get_pressed()

        if current_state == "map":
            if pressed[0]:
                posX, posY = pygame.mouse.get_pos()
                tileMap[posX//grandSize][posY//grandSize].on = 1
            elif pressed[2]:
                posX, posY = pygame.mouse.get_pos()
                tileMap[posX//grandSize][posY//grandSize].on = 0
                
        screen.fill((255,255,255))
        for y in range(512/grandSize):
            for x in range(512/grandSize):
                TILE = tileMap[x][y]
                TILE.update(tileMap)
                TILE.render(screen)

        for CHARACTER in enemy_lst:
            CHARACTER.render(screen)
        
        pygame.draw.circle(screen, (255, 255, 255), (int(start_pos[0] * grandSize), int(start_pos[1] * grandSize)), 8, 2)
        pygame.draw.circle(screen, (0, 255, 0), (int(goal_pos[0] * grandSize), int(goal_pos[1] * grandSize)), 8, 2)

        pygame.display.update()
        pygame.display.set_caption("level: " + save_map_name + ". State: " + current_state + ". Hit F3 to save")
        
    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:"
        print ">>> python marchingTest.py FILENAME\n"
        print "where FILENAME is what the level will be saved as"
    else:
        main()
