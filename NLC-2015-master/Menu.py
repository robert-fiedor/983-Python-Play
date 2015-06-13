import pygame,ImageFuncs,webbrowser



class Menu(object):
    """handles everything about the menu; from
        storing and blitting text to handling
        input."""

    def __init__(self, ss):
        """Creates the Menu, pretty self-explainitory"""
        
        self.w, self.h = ss

        self.menu_font = pygame.font.Font("pixelFont.ttf", 25)
        self.header_font = pygame.font.Font("pixelFont.ttf", 32)
        self.footer_font = pygame.font.Font("pixelFont.ttf", 16)
        self.in_between_font = pygame.font.Font("pixelFont.ttf", 20)

        self.texts = ["START", "LEVEL SELECT", "HELP", "LINKS", "CREDITS", "QUIT"]

        #self.title = "NLC Game and Simulation Submission - 2015"
        self.title = "Sector Shoot 'em up - NLC Submission 2015"

        self.footer = "Open source project. NickandNicksGames 2015"

        self.text_rects = []
        self.title_render = self.header_font.render(self.title, True, (255, 255, 255))
        self.title_rect = self.title_render.get_rect()
        self.title_rect.center = (self.w / 2, self.title_rect.h)
        self.clicked = False
        self.clicked_time = 0

        self.img = pygame.image.load("res/base.png").convert()
        self.ImageFuncs = ImageFuncs.ImageFuncs(32,32,self.img)
        
        self.backdrop = pygame.image.load("res/backdrop.png").convert()

        self.text_rects.append(self.title_rect)

        for TEXT in self.texts:
            TEXT_render = self.menu_font.render(TEXT, True, (255, 255, 255))
            TEXT_index = self.texts.index(TEXT)
            
            TEXT_rect = TEXT_render.get_rect()
            TEXT_rect.center = (self.w / 2,
                    150 + TEXT_rect.h * TEXT_index * 3)

            self.text_rects.append(TEXT_rect)

        self.footer_render = self.footer_font.render(self.footer, True, (255, 255, 255))
        self.footer_rect = self.footer_render.get_rect()
        self.footer_rect.center = (self.w / 2, self.h - self.footer_rect.h)
        
        self.text_rects.append(self.footer_rect)

        self.draw_rect = None

    def handle_mouse_input(self, pos, buttons, help = False, rects = []):
        if help == False:
            self.draw_rect = None
            for RECT in self.text_rects:
                if RECT.collidepoint(pos):
                    self.draw_rect = RECT
                    if buttons[0]:
                        return self.text_rects.index(RECT)

        else:
            if buttons[0]:
                for RECT in rects:
                    if RECT.collidepoint(pos):
                        return rects.index(RECT)

        return None

    def help_screen(self,screen,mouse_pos):
        screen.fill((0,0,0))
        menu_cursor_image = self.ImageFuncs.get_image(3, 1)
        menu_cursor_image.set_colorkey((255, 0, 255))

        open_file = open("text files/helptxt2.txt", 'r')
        linelst =[]
        contents = open_file.readlines()
        for i in range(len(contents)):
             linelst.append(contents[i].strip('\n'))
        for i in linelst:
            if i == '':
                #linelst.pop(linelst.index(i))
                pass
        open_file.close()



        for x, i in enumerate(linelst):
            txt = self.footer_font.render(linelst[x], True, (255, 255, 255))
            txt_rect = txt.get_rect()
            txt_rect.center = (self.w / 2, 50 + txt_rect.h * x * 1.5)
            screen.blit(txt,txt_rect)

        txt = self.menu_font.render("Press ESCAPE to go back", True, (255, 0, 255))
        txt_rect = txt.get_rect()
        txt_rect.center = (self.w / 2, self.h - 50)
        screen.blit(txt,txt_rect)
        screen.blit(menu_cursor_image, (mouse_pos[0]-16, mouse_pos[1]-16))


    def links(self,screen,mouse_pos,tick):
        screen.fill((0,0,0))
        self.img_lst = []
        self.img_lst.append(self.ImageFuncs.get_image(0,1))
        self.img_lst.append(self.ImageFuncs.get_image(1,2))
        self.img_lst.append(self.ImageFuncs.get_image(0,3))
        self.img_lst.append(self.ImageFuncs.get_image(2,2))
        menu_cursor_image = self.ImageFuncs.get_image(3, 1)
        menu_cursor_image.set_colorkey((255, 0, 255))

        open_file = open("text files/links.txt", 'r')
        linelst =[]
        text_rects = []
        contents = open_file.readlines()
        for i in range(len(contents)):
             linelst.append(contents[i].strip('\n'))
        for i in linelst:
            if i == '':
                linelst.pop(linelst.index(i))
        open_file.close()



        for i in self.img_lst:
            i.set_colorkey((255,0,255))
            index = self.img_lst.index(i)
            screen.blit(i,(350, 100 + i.get_height() * index * 3))
            txt = self.menu_font.render(linelst[index], True, (255, 255, 255))
            txt_rect = txt.get_rect()
            text_rects.append(txt_rect)
            txt_rect.midleft = (460,117 + i.get_height() * index * 3)
            screen.blit(txt,txt_rect)

        txt = self.menu_font.render("Press ESCAPE to go back", True, (255, 0, 255))
        txt_rect = txt.get_rect()
        txt_rect.center = (self.w / 2, self.h - 50)
        screen.blit(txt,txt_rect)
        screen.blit(menu_cursor_image, (mouse_pos[0]-16, mouse_pos[1]-16))

        option = self.handle_mouse_input(mouse_pos, pygame.mouse.get_pressed(),True,text_rects)
        if option is not None:
            if option == 0:
                webbrowser.open_new(r"http://en.wikipedia.org/wiki/Computer_virus")
                return "link"
            if option == 1:
                webbrowser.open_new(r"http://en.wikipedia.org/wiki/Rootkit")
                return "link"
            if option == 2:
                webbrowser.open_new(r"http://en.wikipedia.org/wiki/Spambot")
                return "link"
            if option == 3:
                webbrowser.open_new(r"http://en.wikipedia.org/wiki/Botnet")
                return "link"

    def level_select(self, surface, mouse_pos, tick, main_world):
        surface.fill((0, 0, 0))
        self.img = pygame.image.load("res/base.png").convert()
        self.ImageFuncs = ImageFuncs.ImageFuncs(32,32,self.img)
        menu_cursor_image = self.ImageFuncs.get_image(3, 1)
        menu_cursor_image.set_colorkey((255, 0, 255))
 
        to_return = None

        x = y = 0
        for i in main_world.levels:
            level_img = pygame.Surface((96, 96))
            level_img.fill((200, 200, 200))

            level_rect = level_img.get_rect()
            level_img.blit(self.in_between_font.render(i.title(), True, (20, 20, 20)), (2, 2))
            level_rect.center = (128 + 160 * x, 128 + 160 * y)
            surface.blit(level_img, level_rect)

            x += 1
            if x == 5:
                x = 0
                y += 1

            pressed = pygame.mouse.get_pressed()
            if pressed[0] and level_rect.collidepoint(mouse_pos):
                to_return = i
        surface.blit(menu_cursor_image, (mouse_pos[0]-16, mouse_pos[1]-16))

        return to_return

    def credits(self,surface,mouse_pos,tick):
        surface.fill((0,0,0))
        menu_cursor_image = self.ImageFuncs.get_image(3, 1)
        menu_cursor_image.set_colorkey((255, 0, 255))
        open_file = open("text files/credits.txt", 'r')
        linelst =[]
        contents = open_file.readlines()
        for i in range(len(contents)):
             linelst.append(contents[i].strip('\n'))
        for i in linelst:
            if i == '':
                linelst.pop(linelst.index(i))
        open_file.close()
        for i in linelst:
            index = linelst.index(i)
            txt = self.menu_font.render(linelst[index], True, (255, 255, 255))
            txt_rect = txt.get_rect()
            txt_rect.midleft = (100,30 * index + 30)
            surface.blit(txt,txt_rect)

        txt = self.menu_font.render("Press ESCAPE to go back", True, (255, 0, 255))
        txt_rect = txt.get_rect()
        txt_rect.center = (self.w / 2, self.h - 50)
        surface.blit(txt,txt_rect)

        surface.blit(menu_cursor_image, (mouse_pos[0]-16, mouse_pos[1]-16))

    def render(self, surface):
        """Renders the text stored in the class to the screen"""

        surface.blit(self.backdrop, (0, 0))

        surface.blit(self.title_render, self.title_rect)

        for TEXT in self.texts:
            TEXT_render = self.menu_font.render(TEXT, True, (255, 255, 255))
            TEXT_index = self.texts.index(TEXT)
            
            TEXT_rect = TEXT_render.get_rect()
            TEXT_rect.center = (self.w / 2, 
                    150 + TEXT_rect.h * TEXT_index * 3)

            surface.blit(TEXT_render, TEXT_rect)

        surface.blit(self.footer_render, self.footer_rect)

        if self.draw_rect is not None:
            pygame.draw.rect(surface, (255, 255, 255), self.draw_rect.inflate(6, 6), 2)
