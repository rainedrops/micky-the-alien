import pygame as pg
import random as rd
import pytmx
from settings import *
from sprites import *
from os import path
import json


class TiledMap:
    def __init__(self, filename, mapwidth, mapheight, tile_img_size):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = mapwidth * tile_img_size
        self.height = mapheight * tile_img_size
        self.tmxdata = tm
        self.tile_img_size = tile_img_size
        self.mapwidth = mapwidth
        self.mapheight = mapheight
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tile_img_size,
                                            y * self.tile_img_size))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        temp_surface.fill(bg)
        self.render(temp_surface)
        #temp_surface = pg.transform.scale(temp_surface, (self.mapwidth*TILESIZE, self.mapheight*TILESIZE))
        return temp_surface

class Camera:
    def __init__(self, width, height, mapwidth, mapheight):
        self.camera = pg.Rect(0,0, width, height)
        self.width = width
        self.height = height
        self.mapwidth = mapwidth
        self.mapheight = mapheight

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + WIDTH/2#int(camwidth * TILESIZE / 2)
        y = -target.rect.y + HEIGHT/2#int(camheight * TILESIZE / 2)
        #Scrolling limits
        x = min(0,x)
        y = min(0,y)
        x = max(-self.mapwidth*TILESIZE + WIDTH, x)#max(-((self.mapwidth - camwidth)*TILESIZE), x)
        y = max(-self.mapheight*TILESIZE + HEIGHT, y)#max(-((self.mapheight - camheight)*TILESIZE), y)
        self.offsetx = -x + WIDTH
        self.camera = pg.Rect(x, y, self.width, self.height)

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width,height))#.convert_alpha()
        image.fill(bg)
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        image.set_colorkey(bg)
        return image

game_folder = path.dirname(__file__)
save_folder = path.join(game_folder, 'saves')

class Game:
    def __init__(self):
        #Initializing
        pg.init()
        pg.mixer.init(4100, -16, 2, 2048)
        self.font_name = pg.font.match_font('terminator two')
        self.screen = pg.display.set_mode((0,0),pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        #load Data
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'images')
        map_folder = path.join(game_folder, 'maps')
        save_folder = path.join(game_folder, 'saves')
        sound_folder = path.join(game_folder, 'sounds')
        #Loading controls

        #Added on 11/9
        self.letters_d = {
        pg.K_q:'a',
        pg.K_a:'q',
        pg.K_z:'w',
        pg.K_w:'z',
        pg.K_SEMICOLON:'m',
        pg.K_e:'e',
        pg.K_r:'r',
        pg.K_t:'t',
        pg.K_y:'y',
        pg.K_u:'u',
        pg.K_i:'i',
        pg.K_o:'o',
        pg.K_p:'p',
        pg.K_s:'s',
        pg.K_d:'d',
        pg.K_f:'f',
        pg.K_g:'g',
        pg.K_h:'h',
        pg.K_j:'j',
        pg.K_k:'k',
        pg.K_l:'l',
        pg.K_x:'x',
        pg.K_c:'c',
        pg.K_v:'v',
        pg.K_b:'b',
        pg.K_n:'n'
        }

        #Added on 11/9
        with open(path.join(save_folder,'savefile_js.txt'), 'r') as f:
            self.datasave = json.load(f)

        with open(path.join(save_folder,'controls_js.txt'), 'r') as f:
            self.controls = json.load(f)


        #Loading Sounds
        self.son_cris = pg.mixer.Sound(path.join(sound_folder, "cris.wav"))
        self.son_coin = pg.mixer.Sound(path.join(sound_folder, "pièce2.wav"))
        self.son_gem = pg.mixer.Sound(path.join(sound_folder, "gemme.wav"))
        self.son_jump = pg.mixer.Sound(path.join(sound_folder, "saut.wav"))
        self.son_marcher = pg.mixer.Sound(path.join(sound_folder, "marcher.wav"))
        self.son_tir = pg.mixer.Sound(path.join(sound_folder, "tir.wav"))
        self.son_win = pg.mixer.Sound(path.join(sound_folder, "victoire.wav"))
        self.son_degat = pg.mixer.Sound(path.join(sound_folder, "dégat.wav"))
        self.son_defaite = pg.mixer.Sound(path.join(sound_folder,"défaite.wav"))
        self.son_epee = pg.mixer.Sound(path.join(sound_folder,"épée.wav"))
        #self.son_bomb = pg.mixer.Sound(path.join(sound_folder, "bombe.wav"))

        self.son_epee.set_volume(0.8)
        self.son_defaite.set_volume(0.5)
        self.son_win.set_volume(0.2)
        self.son_jump.set_volume(0.7)
        self.son_degat.set_volume(0.4)
        self.son_coin.set_volume(0.1)
        self.son_marcher.set_volume(0.02)
        self.musique = pg.mixer.Sound(path.join(sound_folder,"hyrule castle.wav"))
        #pg.mixer.music.load((sound_folder, "hyrule castle.mp4"))
        #pg.mixer.music.set_volume(0.4)
        #Loading spritesheets
        self.tiles_spritesheet = Spritesheet(path.join(img_folder,'tiles_spritesheet.png'))
        self.builds_spritesheet = Spritesheet(path.join(img_folder,'builds_spritesheet.png'))
        self.items_spritesheet = Spritesheet(path.join(img_folder,'items_spritesheet.png'))
        self.player_spritesheet = Spritesheet(path.join(img_folder,'player_spritesheet.png'))
        self.UI_spritesheet = Spritesheet(path.join(img_folder,'hud_spritesheet.png'))
        self.mob_spritesheet = Spritesheet(path.join(img_folder,'mob_spritesheet.png'))
        self.builds_alt = Spritesheet(path.join(map_folder,'buildings background.png'))

        self.heart_full = self.UI_spritesheet.get_image(0, 94, 53, 45)
        self.heart_empety = self.UI_spritesheet.get_image(0, 47, 53, 45)
        self.gem_true = self.UI_spritesheet.get_image(98, 223, 46, 36)
        self.gem_false = self.UI_spritesheet.get_image(104, 0, 46, 36)

        self.player_img = self.player_spritesheet.get_image(67, 196, 66, 92)
        self.sword_img = pg.image.load(path.join(img_folder, 'sword.png')).convert_alpha()
        self.gun_img = pg.image.load(path.join(img_folder, 'gun.png')).convert_alpha()
        self.coinblock = pg.image.load(path.join(img_folder, 'boxCoin.png')).convert_alpha()
        self.coinblock_open = pg.image.load(path.join(img_folder, 'boxCoin_disabled.png')).convert_alpha()
        self.itemblock = pg.image.load(path.join(img_folder, 'boxItem.png')).convert_alpha()
        self.itemblock_open = pg.image.load(path.join(img_folder, 'boxItem_disabled.png')).convert_alpha()

        self.grass = self.tiles_spritesheet.get_image(576, 576, 70, 70)
        self.dirt = self.tiles_spritesheet.get_image(720, 864, 70, 70)
        self.menu_img = pg.image.load(path.join(img_folder, 'menu_img.png'))
        self.menu_img = pg.transform.scale(self.menu_img, (WIDTH, HEIGHT))
        self.go_img = pg.image.load(path.join(img_folder, 'go_img.jpg'))
        self.go_img = pg.transform.scale(self.go_img, (WIDTH, HEIGHT))
        self.win_img = pg.image.load(path.join(img_folder, 'victoire img.png'))
        self.win_img = pg.transform.scale(self.win_img, (WIDTH, HEIGHT))

        self.keys_img = {
        'green':self.items_spritesheet.get_image(135, 161, 60, 36),
        'red':self.items_spritesheet.get_image(77, 450, 60, 36),
        'blue':self.items_spritesheet.get_image(136, 15, 60, 36),
        'yellow':self.items_spritesheet.get_image(77, 378, 60, 36)
        }

        self.lockers_img = {
        'green':self.tiles_spritesheet.get_image(72, 576, 70, 70),
        'red':self.tiles_spritesheet.get_image(432, 360, 70, 70),
        'blue':self.tiles_spritesheet.get_image(432, 504, 70, 70),
        'yellow':self.tiles_spritesheet.get_image(432, 288, 70, 70)
        }

        self.fake_walls_img = {
        'grass':self.tiles_spritesheet.get_image(504, 576, 70, 70),
        'dirt':self.tiles_spritesheet.get_image(576, 864, 70, 70),
        'stone':self.builds_spritesheet.get_image(490, 0, 70, 70),
        'ground':self.builds_spritesheet.get_image(490, 140, 70, 70),
        'castle1':self.tiles_spritesheet.get_image(504, 288, 70, 70),
        'sand':self.builds_alt.get_image(70, 0, 70, 70)
        }
    def main_menu(self):
        self.password = ''
        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.fill(bg)
                self.screen.blit(self.menu_img, (0,0))
                self.draw_text('welcome to the game', 80, LIGHTGREY, WIDTH/2, HEIGHT/8)
                self.draw_button('play', 50, WHITE, WIDTH/8, HEIGHT*3/8,'new', red, RED)
                self.draw_button('options', 50, WHITE, WIDTH/8, HEIGHT*4/8,'options', red, RED)
                self.draw_button('rules', 50, WHITE, WIDTH/8, HEIGHT*5/8,'rules', red, RED)
                self.draw_button('credits', 50, WHITE, WIDTH/8, HEIGHT*6/8,'credits', red, RED)
                self.draw_button('quit game', 50, WHITE, WIDTH/8, HEIGHT*7/8,'quit', red, RED)

                pg.display.flip()
                if self.callback:
                    if self.callback[0] == 'new':
                        return self.level_menu()
                    elif self.callback[0] == 'options':
                        return self.option_menu()
                    elif self.callback[0] == 'rules':
                        return self.show_rules()
                    elif self.callback[0] == 'credits':
                        return self.show_credits()
                    elif self.callback[0] == 'quit':
                        self.running = False

    def show_rules(self):
        self.password = ''
        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.blit(self.menu_img, (0,0))
                self.draw_text('RULES', 80, LIGHTGREY, WIDTH/2, HEIGHT/8)
                self.draw_text('This game is easy : you are controlling a caracter,\nand you have to get to the end of the level without dying, bytrying to do\nthe best possible score and finding hidden items.\nmove your caracter with ZQD (default), use abilities with JKL (default) ', 40, DARKGREY, WIDTH/2, HEIGHT/2)
                self.draw_button('back', 30, WHITE, WIDTH/16, HEIGHT/16,'back')
                pg.display.flip()
                if self.callback:
                    if self.callback[0] == 'back':
                        return self.main_menu()

    def level_menu(self):
        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.blit(self.menu_img, (0,0))
                self.draw_text('LEVEL SELECTION', 50, LIGHTGREY, WIDTH/2, HEIGHT/8)
                self.draw_button('Level 1', 50, WHITE, WIDTH/2, HEIGHT*3/8,'1', red, RED, self.datasave['1']["state"])
                self.draw_button('Level 2', 50, WHITE, WIDTH/2, HEIGHT*4/8,'2', red, RED, False)
                self.draw_button('Level 3', 50, WHITE, WIDTH/2, HEIGHT*5/8,'3', red, RED, self.datasave['3']["state"])
                self.draw_button('Level 4', 50, WHITE, WIDTH/2, HEIGHT*6/8,'4', red, RED, self.datasave['4']["state"])
                self.draw_button('back', 30, WHITE, WIDTH/16, HEIGHT/16,'back')

                #Display acheivements
                for i, lv in enumerate(self.datasave):
                    self.draw_text(str(self.datasave[str(i+1)]["score"]), 80, DARKGREY, WIDTH*3/8 - 40, HEIGHT*(3+i)/8)

                for i, star in enumerate(self.datasave['1']["star"]):
                    if star:
                        self.screen.blit(self.gem_true, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*3/8 - 18))
                    else:
                        self.screen.blit(self.gem_false, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*3/8 - 18))


                for i, star in enumerate(self.datasave['2']["star"]):
                    if star:
                        self.screen.blit(self.gem_true, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*4/8 - 18))
                    else:
                        self.screen.blit(self.gem_false, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*4/8 - 18))


                for i, star in enumerate(self.datasave['3']["star"]):
                    if star:
                        self.screen.blit(self.gem_true, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*5/8 - 18))
                    else:
                        self.screen.blit(self.gem_false, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*5/8 - 18))


                for i, star in enumerate(self.datasave['4']["star"]):
                    if star:
                        self.screen.blit(self.gem_true, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*6/8 - 18))
                    else:
                        self.screen.blit(self.gem_false, (WIDTH*5/8 + WIDTH*i/32, HEIGHT*6/8 - 18))

                pg.display.flip()
                if self.callback:
                    if self.callback[0] == '1':
                        return self.new('level 1 final.tmx', 150, 20, 70, '1')
                    elif self.callback[0] == '2':
                        return self.new('level 2.tmx', 100, 20, 21, '2')
                    elif self.callback[0] == '3':
                        return self.new('level 3 final.tmx', 119, 31, 70, '3')
                    elif self.callback[0] == '4':
                        return self.new('level 4 final.tmx', 150, 50, 70, '4')
                    elif self.callback[0] == 'back':
                        return self.main_menu()

    def option_menu(self):
        def reset():
            self.datasave = {
                            "1": {"state": True, "star": [False, False, False], "score": 0, "next":"3"},
                            "2": {"state": False, "star": [False, False, False], "score": 0, "next":"1"},
                            "3": {"state": False, "star": [False, False, False], "score": 0, "next":"4"},
                            "4": {"state": False, "star": [False, False, False], "score": 0, "next":"1"}
                            }

        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.fill(bg)
                self.screen.blit(self.menu_img, (0,0))
                self.draw_text('OPTIONS', 80, LIGHTGREY, WIDTH/2, HEIGHT/8)
                self.draw_button('controls', 50, WHITE, WIDTH/6, HEIGHT*3/8,'bindings',red, RED)
                self.draw_button('use password', 50, WHITE, WIDTH/6, HEIGHT*4/8,'cheat',red, RED)
                self.draw_button('contact the dev', 50, WHITE, WIDTH/6, HEIGHT*5/8,'report',red, RED)
                self.draw_button('reset saves', 50, WHITE, WIDTH/6, HEIGHT*6/8,'reset',red, RED)
                self.draw_button('back', 30, WHITE, WIDTH/16, HEIGHT/16, 'back')

                pg.display.flip()

                if self.callback:
                    if self.callback[0] == 'back':
                        return self.main_menu()
                    elif self.callback[0] == 'bindings':
                        return self.control_menu()
                    elif self.callback[0] == 'cheat':
                        return self.password_screen()
                    elif self.callback[0] == 'report':
                        pass
                    elif self.callback[0] == 'reset':
                        reset()

    def control_menu(self):
        def reset():
            #Added on 11/9
            self.controls = {"up":119,"down":115,"left":97,"right":100,"power1":106,"power2":107,"power3":108}
            with open(path.join(save_folder,'controls_js.txt'), 'w') as f:
                            json.dump(self.controls, f)

        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.fill(bg)
                self.screen.blit(self.menu_img, (0,0))
                self.draw_text('CHANGE CONTROLS', 80, LIGHTGREY, WIDTH/2, HEIGHT/8)
                self.draw_button('left', 40, WHITE, WIDTH/4 +80, HEIGHT*2.5/8,'left', green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["left"]], 32, DARKGREY, WIDTH/4 + 100, HEIGHT*2.5/8, 580)

                self.draw_button('right', 40, WHITE, WIDTH/4 +80, HEIGHT*3.5/8,'right', green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["right"]], 32, DARKGREY, WIDTH/4 + 100, HEIGHT*3.5/8, 580)

                self.draw_button('jump', 40, WHITE, WIDTH/4 +80, HEIGHT*4.5/8,'up', green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["up"]], 32, DARKGREY, WIDTH/4 + 100, HEIGHT*4.5/8, 580)

                self.draw_button('crough', 40, WHITE, WIDTH/4 +80, HEIGHT*5.5/8,'down', green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["down"]], 32, DARKGREY, WIDTH/4 + 100, HEIGHT*5.5/8, 580)


                self.draw_button('power 1', 40, WHITE, WIDTH/2 +80, HEIGHT*3/8,'power1',green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["power1"]], 32, DARKGREY, WIDTH/2 + 100, HEIGHT*3/8, 1030)

                self.draw_button('power 2', 40, WHITE, WIDTH/2 +80, HEIGHT*4/8,'power2',green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["power2"]], 32, DARKGREY, WIDTH/2 + 100, HEIGHT*4/8, 1030)

                self.draw_button('power 3', 40, WHITE, WIDTH/2 +80, HEIGHT*5/8,'power3',green, GREEN)
                self.draw_text('      current : '+ self.letters_d[self.controls["power3"]], 32, DARKGREY, WIDTH/2 + 100, HEIGHT*5/8, 1030)
                self.draw_button('back', 30, WHITE, WIDTH/16, HEIGHT/16,'back')
                self.draw_button('restore default', 50, WHITE, WIDTH/2, HEIGHT*7/8,'reset',red, RED)

                pg.display.flip()

                if self.callback:
                    if self.callback[0] == 'back':
                        return self.option_menu()
                    elif self.callback[0] == 'reset':
                        reset()
                    else:
                        self.ctrl_input(self.callback[0], pg.time.get_ticks())

    def password_screen(self):
        def unlock(pw):

            if pw == 'iloveraffi' or pw == 'overcomeal':
                self.datasave['3']["state"] = True
                self.datasave['4']["state"] = True
            #elif pw == 'seladeche':
            #    lives += 10

        if self.running:
            self.call = False
            while self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    else:
                        self.call = False
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            unlock(self.password)
                            self.password = ''
                        if event.key == 8:
                            try:
                                pw = list(self.password)
                                del pw[-1]
                                self.password = ''.join(pw)

                            except IndexError:
                                 pass
                        elif len(self.password) < 10:
                            self.password += self.letters_d.get(event.key, "")

                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.fill(bg)
                self.screen.blit(self.menu_img, (0,0))

                self.draw_text('ENTER PASSWORD', 80, WHITE, WIDTH/2, HEIGHT/8)
                self.draw_text(self.password.upper() + '_'*(10-len(self.password)), 140, BLACK, WIDTH/2, HEIGHT/2)
                self.draw_button('back', 30, WHITE, WIDTH/16, HEIGHT/16,'back')

                pg.display.flip()

                if self.callback:
                    if self.callback[0] == 'back':
                        return self.option_menu()

    def ctrl_input(self, assign, time):
        if self.running:
            while self.running:
                if pg.time.get_ticks() - time > 6000:
                    return
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    if event.type == pg.KEYDOWN:
                        #Added on 11/9
                        self.controls[assign] = event.key

                        with open(path.join(save_folder,'controls_js.txt'), 'w') as f:
                            json.dump(self.controls, f)
                        return

    def draw_button(self, text, size, color, x, y, func, bg=None, Bg=None, state = True):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect()
        rect.center = (x, y)
        #checking if the mouse is inside the button rect
        if rect[0] + rect[2] > self.mouse[0] > rect[0] and rect[1] + rect[3] > self.mouse[1] > rect[1] and state:
            #upgrading the size of the writing, but have to redo all the process
            font = pg.font.Font(self.font_name, int(size*1.2))
            text_surface = font.render(text, True, color)
            rect = text_surface.get_rect()
            rect.center = (x, y)
            #changing the bg color
            if Bg:
                pg.draw.rect(self.screen, Bg, rect)
            hover = True
        elif not state:
            pg.draw.rect(self.screen, dark_red, rect)
            hover = False
        else:
            if bg:
                pg.draw.rect(self.screen, bg, rect)
            hover = False
        self.screen.blit(text_surface, rect)
        if hover and self.call:
            self.callback.append(func)

    def new(self, level, mapw, maph, size, index):
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')
        sound_folder = path.join(game_folder, 'sounds')
        self.name = level
        self.size = size
        self.level = index
        self.mapwidth = mapw
        self.mapheight = maph
        #loading appropriate music
        global bg
        if self.level == '1':
            bg = (30,144,255)
            #self.musique = pg.mixer.Sound(path.join(sound_folder,"piano.wav"))
            #self.musique.set_volume(0.01)
        if self.level == '3':
            self.musique = pg.mixer.Sound(path.join(sound_folder,"hyrule castle.wav"))
            self.musique.set_volume(0.05)
        if self.level == '4':
            bg = (135,206,250)
            self.musique = pg.mixer.Sound(path.join(sound_folder,"gerudo town.wav"))
            self.musique.set_volume(0.05)

        #Loading TiledMap
        self.map = TiledMap(path.join(map_folder, level), mapw, maph, size)
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        #self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.fake_walls_1 = pg.sprite.Group()
        self.fake_walls_2 = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.ladders = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.traps = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        # Player Stats related to the game
        self.win = False
        self.back_to_menu = False
        self.paused = False
        self.coin_count = 0
        self.gem_count = 0
        self.score = 0
        self.stars = [False, False, False]
        self.pup_gun = False
        self.pup_bomb = False

        self.keys = {
        'green':False,
        'red':False,
        'blue':False,
        'yellow':False
        }
        #Reading Trough TiledMap Objects layer
        for item in self.map.tmxdata.objects:
            if item.name == 'player':
                self.player = Player(self, item.x, item.y)
            if item.name == 'obstacle':
                Obstacle(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste)
            if item.name == 'box':
                if item.type == 'coin':
                    Coin_block(self, item.x * cste, item.y * cste,
                                item.width * cste,item.height * cste)
                if item.type == 'gem':
                    Powerup_block(self, item.x * cste, item.y * cste,
                                item.width * cste,item.height * cste)
            if item.name == 'gem':
                Powerup(self, item.x * cste, item.y * cste,
                            item.width * cste,item.height * cste)
            if item.name == 'tempo':
                Temporary_obs(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste)
            if item.name == 'platform':
                Platform(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste)
            if item.name == 'moving':
                Moving_platform(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste, item.type)
            if item.name == 'fake wall':
                Fake_wall(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste, item.type)
            if item.name == 'fragile':
                Fragile(self, item.x * cste, item.y * cste,
                        item.width * cste,item.height * cste)
            if item.name == 'coin':
                Coin(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'star':
                Star(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste, item.type)
            if item.name == 'life':
                Life(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'ladder':
                Ladder(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'slime':
                Slime(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste, item.type)
            if item.name == 'fish':
                Fish(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'idle':
                self.oui = Idle_Mob(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'spike':
                Spike(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste, item.type)
            if item.name == 'launcher':
                Launcher(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste, item.type)
            if item.name == 'lava':
                Lava(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'lavaball':
                Lavaball(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste, item.type)
            if item.name == 'springboard':
                Springboard(self, item.x * cste, item.y * cste,
                item.width * cste,item.height * cste)
            if item.name == 'button':
                Button(self, item.x * cste, item.y * cste,
                int(item.width * cste), int(item.height * cste), item.type)
            if item.name == 'key':
                Key(self, item.x * cste, item.y * cste,
                int(item.width * cste), int(item.height * cste), item.type)
            if item.name == 'locked':
                Locker(self, item.x * cste, item.y * cste,
                int(item.width * cste), int(item.height * cste), item.type)
            if item.name == 'end':
                self.end = End(self, item.x * cste, item.y * cste,
                                item.width * cste, item.height * cste)
        self.camera = Camera(WIDTH, HEIGHT, mapw, maph)
        #pg.mixer.music.play(loops=-1)
        self.musique.play()
        self.run()

    def run(self):
        #GameLoop
        self.playing = True
        self.drawhitboxes = False#related to hitbox secret function
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            if not self.paused: #makes the game pause
                self.update()
            self.draw()
        #stop background music when gameloop stops
        self.musique.stop()
        self.game_over()

    def events(self):
        for event in pg.event.get():
            #Close Window
            self.call = False
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.call = True
            if event.type == pg.KEYDOWN:
                if event.key == 27:
                    self.playing == False
                self.running == False
                #######################/!\/!\/!\/!\/!\/!\/!\#########################
                #if event.key == pg.K_f:
                #    self.drawhitboxes = not self.drawhitboxes
                #######################/!\/!\/!\/!\/!\/!\/!\#########################
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if not self.player.hitting and not self.player.shooting:
                    if event.key == pg.K_SPACE or event.key == self.controls["up"]:
                        self.player.jump()
                    if event.key == self.controls["power1"]:
                        self.player.swordhit()
                    if event.key == self.controls["power2"]:
                        if self.pup_gun:
                            self.player.shoot()
                    if event.key == self.controls["power3"]:
                        if self.pup_bomb:
                            self.player.bomb()

    def update(self):
        self.render_fake_walls_1 = True
        self.render_fake_walls_2 = True
        # Enable abilities
        if self.gem_count >= 1:
            self.pup_gun = True
        if self.gem_count >= 2:
            self.pup_bomb = True

        #Collision chacks for mob and player damage
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            self.son_cris.play()
            mob.lives -= 1
            mob.hurt = pg.time.get_ticks()
        #Player damage
        hits = pg.sprite.spritecollide(self.player, self.mobs, False,
                        pg.sprite.collide_mask) + pg.sprite.spritecollide(self.player, self.traps, False)
        if hits :
            self.player.damaged()

        #Game update
        self.all_sprites.update()
        self.obstacles.update()
        self.fake_walls_1.update()
        self.fake_walls_2.update()
        self.lava.update()
        self.end.update()
        #Camera
        self.camera.update(self.player)
        # Game Over
        if self.player.lives == 0 or self.player.rect.top > self.mapheight * TILESIZE:
            self.playing = False
            self.son_defaite.play()

    def draw(self):
        #pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #pg.display.set_caption(str(self.oui.distance))#rect.centerx - self.oui.root))
        self.screen.fill(LIGHTBLUE)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            try:
                if not sprite.render:
                    pass
                else:
                    self.screen.blit(sprite.image, self.camera.apply(sprite))
            except:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

        if self.render_fake_walls_1:
            for sprite in self.fake_walls_1:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
        if self.render_fake_walls_2:
            for sprite in self.fake_walls_2:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.display_UI()

        if self.drawhitboxes:
            self.draw_hitboxes()
        if self.paused:
            self.draw_pause_UI()

        pg.display.flip()

    def draw_pause_UI(self):
        self.mouse = pg.mouse.get_pos()
        self.callback = []
        self.dim_screen = pg.Surface((WIDTH,HEIGHT)).convert_alpha()
        self.dim_screen.fill((0,0,0,150))
        self.screen.blit(self.dim_screen, (0,0))
        self.draw_text('PAUSED', 120, LIGHTBLUE, WIDTH/2, HEIGHT/4)
        self.draw_button('continue', 70, DARKWHITE, WIDTH/2, HEIGHT/2,'continue')
        self.draw_button('back to main menu', 70, DARKWHITE, WIDTH/2, HEIGHT*5/8,'menu')
        self.draw_button('quit game', 70, DARKWHITE, WIDTH/2, HEIGHT*6/8,'quit')

        pg.display.flip()

        if self.callback:
            if self.callback[0] == 'continue':
                self.paused = False
            elif self.callback[0] == 'menu':
                #self.paused = False
                self.playing = False
                self.back_to_menu = True
            elif self.callback[0] == 'quit':
                self.paused = False
                self.running = False
                self.playing = False

    def display_UI(self):
        self.numbers_list = [self.UI_spritesheet.get_image(230, 0, 30 ,38),
                            self.UI_spritesheet.get_image(196, 41, 26, 37),
                            self.UI_spritesheet.get_image(55, 98, 32, 38),
                            self.UI_spritesheet.get_image(239, 80, 28, 38),
                            self.UI_spritesheet.get_image(238, 122, 29, 38),
                            self.UI_spritesheet.get_image(238, 162, 28, 38),
                            self.UI_spritesheet.get_image(230, 40, 30, 38),
                            self.UI_spritesheet.get_image(226, 206, 32, 39),
                            self.UI_spritesheet.get_image(192, 206, 32, 40),
                            self.UI_spritesheet.get_image(196, 0, 32, 39)]

        for i in range(self.player.lives):
            self.screen.blit(self.heart_full,  (10 + 55*i, 10, 53, 45))
        for i in range(self.player.lives, 4):
            self.screen.blit(self.heart_empety,  (10 + 55*i, 10, 53, 45))

        self.screen.blit(self.numbers_list[self.score // 10000], (10, 65))
        self.screen.blit(self.numbers_list[(self.score%10000) // 1000], (40, 65))
        self.screen.blit(self.numbers_list[(self.score%1000) // 100], (70, 65))
        self.screen.blit(self.numbers_list[(self.score%100) // 10], (100,65))
        self.screen.blit(self.numbers_list[self.score % 10], (130,65))
        self.screen.blit(self.UI_spritesheet.get_image(55, 0, 47, 47), (10, 110))
        self.screen.blit(self.UI_spritesheet.get_image(0, 239, 30, 28), (60, 118))
        self.screen.blit(self.numbers_list[self.coin_count // 10], (90, 114))
        self.screen.blit(self.numbers_list[self.coin_count % 10], (120, 114))

        self.screen.blit(self.UI_spritesheet.get_image(98, 147, 46, 36), (10, 165))
        self.screen.blit(self.UI_spritesheet.get_image(0, 239, 30, 28), (60, 164))
        self.screen.blit(self.numbers_list[self.gem_count], (90, 158))

        if self.pup_gun:
            for i in range(self.player.gun_ammo):
                self.screen.blit(self.items_spritesheet.get_image(0, 553, 19, 14),  (10 + 20*i, 210))

        if self.pup_bomb:
            for i in range(self.player.bomb_ammo):
                self.screen.blit(self.items_spritesheet.get_image(432, 432, 70, 70), (10 + 70*i, 230))

        if self.keys["green"]:
            self.screen.blit(self.UI_spritesheet.get_image(192, 122, 44, 40), (WIDTH-54, 10))
        else:
            self.screen.blit(self.UI_spritesheet.get_image(104, 38, 44, 40), (WIDTH-54, 10))

    def draw_hitboxes(self):
        for obstacle in self.obstacles:
            pg.draw.rect(self.screen, RED, self.camera.apply_rect(obstacle.rect), 1)
        for obstacle in self.platforms:
            pg.draw.rect(self.screen, (200, 30, 30), self.camera.apply_rect(obstacle.rect), 1)
        for obstacle in self.ladders:
            pg.draw.rect(self.screen, ORANGE, self.camera.apply_rect(obstacle.rect), 1)
        for coin in self.coins:
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(coin.rect), 1)
            #pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(coin.hit_rect), 1)
        for item in self.powerups:
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(item.rect), 1)
            #pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(item.hit_rect), 1)
        for mob in self.traps:
            pg.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(mob.rect), 1)
        for mob in self.mobs:
            pg.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(mob.rect), 1)
        pg.draw.rect(self.screen, BLUE, self.camera.apply_rect(self.player.rect), 1)
        for bullet in self.bullets:
            pg.draw.rect(self.screen, BLUE, self.camera.apply_rect(bullet.rect), 1)
        pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(self.end.rect), 1)

    def draw_text(self, text, size, color, x, y, stick = None):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        if stick:
            text_rect.left = stick
        self.screen.blit(text_surface, text_rect)

    def write_data(self):

        #Added on 11/9
        self.datasave[self.datasave[self.level]["next"]]["state"] = True
        if self.datasave[self.level]["score"] < self.score:
            self.datasave[self.level]["score"] = self.score
        for i, star in enumerate(self.stars):
            if star:
                self.datasave[self.level]["star"][i] = True


        with open(path.join(save_folder,'savefile_js.txt'), 'w') as f:
            json.dump(self.datasave, f)

    def end_screen(self):
        self.draw_text(str(self.win), 40, RED, 500, 500)

        self.son_win.play()
        if self.running:
            self.waiting = True
            while self.waiting:
                self.call = False
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    if event.type == pg.QUIT:
                        self.waiting = False
                        self.running = False
                    self.mouse = pg.mouse.get_pos()
                    self.callback = []
                    self.screen.blit(self.win_img, (0,0))
                    self.draw_text('LEVEL COMPLETE', 100, WHITE, WIDTH/2, HEIGHT/5)
                    self.draw_text('score : ' + str(self.score), 80, WHITE, WIDTH/2, HEIGHT*2/5)
                    if self.score > self.datasave[self.level]["score"]:
                        self.draw_text('new highscore !!', 50, WHITE, WIDTH * 5/6, HEIGHT*2/5)

                    self.draw_text('gems   ', 80, WHITE, WIDTH* 9/20, HEIGHT*3/5)
                    for i, star in enumerate(self.stars):
                        if star:
                            self.screen.blit(pg.transform.scale(self.gem_true, (70,50)), (WIDTH/2 + WIDTH*i/20, HEIGHT*3/5 - 26))
                        else:
                            self.screen.blit(pg.transform.scale(self.gem_false, (70,50)), (WIDTH/2 + WIDTH*i/20, HEIGHT*3/5 - 26))
                    self.draw_button('go back to main menu', 60, WHITE, WIDTH/2 , HEIGHT* 4/5, 'back')
                    if self.callback:
                        self.write_data()
                        self.waiting = False
                        self.back_to_menu = True
                    pg.display.flip()

    def show_go_screen(self):
        if self.running:
            self.waiting = True
            while self.waiting:
                self.call = False
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.call = True
                    if event.type == pg.QUIT:
                        self.waiting = False
                        self.running = False
                self.mouse = pg.mouse.get_pos()
                self.callback = []
                self.screen.blit(self.go_img, (0,0))
                self.draw_text('GAME OVER', 100, WHITE, WIDTH/2, HEIGHT/3)
                self.draw_button('retry', 80, WHITE, WIDTH/2, HEIGHT*3/5,'retry')
                self.draw_button('back to main menu', 80, WHITE, WIDTH/2, HEIGHT*4/5,'back')
                pg.display.flip()
                if self.callback:
                    if self.callback[0] == 'retry':
                        self.back_to_menu = False
                        return self.new(self.name, self.mapwidth, self.mapheight, self.size, self.level)
                    if self.callback[0] == 'back':
                        self.back_to_menu = True
                        self.waiting = False


    def game_over(self):
        #Manages all possible actions the program can do when the game is done
        if not self.back_to_menu:
            if self.win == True:
                self.end_screen()
            elif self.win == False:
                self.show_go_screen()

g = Game()
#RunningLoop
while g.running:
    g.main_menu()

pg.quit()
