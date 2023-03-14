import pygame as pg
import random as rd
from settings import *
from os import path
from itertools import chain
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        #self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = game.player_img
        self.image = pg.transform.scale(self.image, (P_W, P_H))
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.lives = 4
        self.last_damage = 0
        self.gun_ammo = 10
        self.bomb_ammo = 4
        self.last_shot = 0
        self.last_reload = 0
        self.last_bomb = 0
        self.bomb_reload = 0
        self.hitting = False
        self.shooting = False
        #self.hurt = False

    def load_images(self):
        self.gun_img = self.game.gun_img
        self.side = 'right'
        self.standing_frames = [self.game.player_spritesheet.get_image(67, 196, 66, 92),
                                self.game.player_spritesheet.get_image(0, 196, 66, 92)]

        pg.transform.scale(self.standing_frames[0],(P_W, P_H))
        pg.transform.scale(self.standing_frames[1],(P_W, P_H))
        for frame in self.standing_frames:
            frame = pg.transform.scale(frame, (P_W, P_H))

        self.walking_frames = [self.game.player_spritesheet.get_image(0, 0, 72, 97),
                                self.game.player_spritesheet.get_image(73, 0, 72, 97),
                                self.game.player_spritesheet.get_image(146, 0, 72, 97),
                                self.game.player_spritesheet.get_image(0, 98, 72, 97),
                                self.game.player_spritesheet.get_image(73, 98, 72, 97),
                                self.game.player_spritesheet.get_image(146, 98, 72, 97),
                                self.game.player_spritesheet.get_image(219, 0, 72, 97),
                                self.game.player_spritesheet.get_image(292, 0, 72, 97),
                                self.game.player_spritesheet.get_image(219, 98, 72, 97),
                                self.game.player_spritesheet.get_image(365, 0, 72, 97),
                                self.game.player_spritesheet.get_image(292, 98, 72, 97)]

        self.walking_frames_r = []
        self.walking_frames_l = []
        for frame in self.walking_frames:
            frame = pg.transform.scale(frame, (P_W, P_H))
            self.walking_frames_l.append(pg.transform.flip(frame, True, False))
            self.walking_frames_r.append(frame)

        self.jump_frame = self.game.player_spritesheet.get_image(438, 93, 67, 94)
        self.jump_frame = pg.transform.scale(self.jump_frame, (P_W, P_H))

        self.hurt_frame = self.game.player_spritesheet.get_image(438, 0, 69, 92)
        self.hurt_frame = pg.transform.scale(self.hurt_frame, (P_W, P_H))

    def animate(self):
        if self.vel.x < 0:
            self.side = 'left'
        elif self.vel.x > 0:
            self.side = 'right'
        bottom = self.rect.bottom
        now = pg.time.get_ticks()
        # jumping animation
        if self.vel.y != 0:
            self.last_update = now
            self.current_frame = 1
            if self.side == 'right':
                self.image = self.jump_frame
            elif self.side == 'left':
                self.image = pg.transform.flip(self.jump_frame, True, False)
        # walking animation
        elif self.vel.x != 0:
            if now - self.last_update > 40:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                if self.side == 'right':
                    self.image = self.walking_frames_r[self.current_frame]
                elif self.side == 'left':
                    self.image = self.walking_frames_l[self.current_frame]
        # idle animation
        else:
            self.current_frame = 7
            if self.side == 'right':
                self.image = self.walking_frames_r[self.current_frame]
            if self.side == 'left':
                self.image = self.walking_frames_l[self.current_frame]

        if now - self.last_damage < 3000:
            if self.side == 'right':
                self.image = self.hurt_frame
            if self.side == 'left':
                self.image = pg.transform.flip(self.hurt_frame, True, False)

        #self.rect = self.image.get_rect()
        #self.rect.bottom = bottom

    def update(self):
        self.mask = pg.mask.from_surface(self.image)
        #Can't do anything if player isn't shooting or hitting grounded
        if self.vel.y !=0 or (not self.hitting and not self.shooting):
            self.acc = vec(0,GRAVITY)
            keys = pg.key.get_pressed()
            if keys [pg.K_LEFT] or keys [self.game.controls["left"]]:
                self.acc.x = -P_ACC
                if self.vel.y == 0:
                    self.game.son_marcher.play()
            if keys [pg.K_RIGHT] or keys [self.game.controls["right"]]:
                self.acc.x = P_ACC
                if self.vel.y == 0:
                    self.game.son_marcher.play()
            if pg.sprite.spritecollideany(self, self.game.ladders):
                if keys [pg.K_SPACE] or keys [self.game.controls["up"]]:
                    self.vel.y = -5
                else:
                    self.vel.y = 3
                self.acc.y = 0
            #if keys [pg.K_DOWN]:
            #    self.acc.y = ACC
            self.animate()
            #Friction slow
            self.acc.x += self.vel.x * P_FRIC
            #Motion equation application
            self.vel += self.acc
            if abs(self.vel.x) < 0.5:
                self.vel.x = 0
            self.pos += self.acc/2 + self.vel
            #Terrain Limit:
            if self.pos.x < P_W/2:
                self.pos.x = P_W/2
            if self.pos.x > self.game.mapwidth*TILESIZE - P_W/2:
                self.pos.x = self.game.mapwidth*TILESIZE - P_W/2

            self.rect.centerx = self.pos.x
            self.wall_collide(self.game.obstacles, 'x')
            self.hovered = pg.sprite.spritecollideany(self, self.game.platforms)
            self.rect.centery = self.pos.y
            self.wall_collide(self.game.obstacles, 'y')

            if not self.hovered :
                if self.vel.y > 0:
                    self.wall_collide(self.game.platforms, 'y')

        #hitting is managed in the swordhit/gunhit section
        #if self.hurt:
        #    try:
        #        self.image.fill((30,144,255,next(self.color_alpha)))
        #        print(self.color_alpha)
        #    except:
        #        self.hurt = False

        self.reload()

    def damaged(self):
        #self.color_alpha = chain(DAMAGE_ALPHA*6)
        hits = pg.sprite.spritecollide(self, self.game.mobs, False,
                        pg.sprite.collide_mask) + pg.sprite.spritecollide(self, self.game.traps, False)
        now = pg.time.get_ticks()
        if hits and now - self.last_damage > 3000:
            self.lives -= 1
            self.last_damage = now
            self.game.son_degat.play()

            if self.vel.x != 0:
                if hits[0].rect.midbottom > self.rect.midbottom:
                    self.vel = vec(P_KB, P_KB /2)
                if hits[0].rect.midbottom < self.rect.midbottom:
                    self.vel = vec(-P_KB, P_KB /2)

            #elif self.vel.x < 0:
            #    self.vel = vec(-P_KB, P_KB /2)
            elif self.vel.x == 0:
                if self.vel.y !=0:
                    fate = rd.randrange(2)
                    if fate:
                        self.vel = vec(P_KB, P_KB / 2)
                    else:
                        self.vel = vec(-P_KB, P_KB / 2)
                elif hits[0].velx > 0:
                    self.vel = vec(-P_KB, P_KB / 2)
                elif hits[0].velx < 0:
                    self.vel = vec(P_KB, P_KB / 2)
                else:
                    if hits[0].rect.midbottom > self.rect.midbottom:
                        self.vel = vec(P_KB, P_KB /2)
                    if hits[0].rect.midbottom < self.rect.midbottom:
                        self.vel = vec(-P_KB, P_KB /2)

    def wall_collide(self,group,dir, spe=False):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, group, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - (P_W/2)
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + (P_W/2)
                self.vel.x = 0
                self.rect.centerx = self.pos.x

        if dir == 'y':
            if not spe:
                hits = pg.sprite.spritecollide(self, group, False)
            if spe:
                hits = pg.sprite.collide_rect(self, group)
                if hits:
                    hits = [group]
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - (P_H/2)
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + (P_H/2)
                self.vel.y = 0
                self.rect.centery = self.pos.y

    def jump(self):
        self.rect.bottom +=1
        hits = pg.sprite.spritecollide(self,self.game.obstacles, False)
        if not self.hovered:
            hits += pg.sprite.spritecollide(self,self.game.platforms, False)
        self.rect.bottom -=1
        if hits:
            self.vel.y = P_JUMP
            self.game.son_jump.play()

    def swordhit(self):
        self.hitting = pg.time.get_ticks()
        if self.side == 'right':
            Sword(self.game, (self.rect.midright[0] - 20,self.rect.midright[1] + 22), 'r')
        if self.side == 'left':
            Sword(self.game, (self.rect.midleft[0] + 20, self.rect.midright[1] + 22), 'l')

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > 300 and self.gun_ammo:
            self.last_shot = now
            self.gun_ammo -= 1
            if self.side == 'right':
                Bullet(self.game, (self.rect.midright[0],self.rect.midright[1] + 16), 'r')
                Gun(self.game, (self.rect.midright[0] - 35,self.rect.midright[1] + 16), 'r')
            if self.side == 'left':
                Bullet(self.game, (self.rect.midleft[0], self.rect.midright[1] + 16), 'l')
                Gun(self.game, (self.rect.midleft[0] + 35, self.rect.midright[1] + 16), 'l')
            self.game.son_tir.play()
            #Used for gun animation
            self.shooting = now

    def bomb(self):
        now = pg.time.get_ticks()
        if now - self.last_bomb > 800 and self.bomb_ammo:
            self.last_bomb = now
            self.bomb_ammo -= 1
            if self.side == 'right':
                Bomb(self.game, self.rect.midright, 'r')
            if self.side == 'left':
                Bomb(self.game, self.rect.midleft, 'l')
            #self.game.son_bomb.play()

    def reload(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > 2000:
            if now - self.last_reload > 400:
                self.last_reload = now
                self.gun_ammo += 1
                self.gun_ammo = min(10, self.gun_ammo)
            if now - self.last_bomb > 4000:
                if now - self.bomb_reload > 1200:
                    self.bomb_reload = now
                    self.bomb_ammo += 1
                    self.bomb_ammo = min(4, self.bomb_ammo)

class Sword(pg.sprite.Sprite):
    def  __init__(self, game, coord, dir):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.rotate(game.sword_img, 90)
        self.rect = self.image.get_rect()
        if dir == 'r':
            self.rect.midleft = coord
            self.image = pg.transform.flip(self.image, True, False)
        if dir == 'l':
            self.rect.midright = coord
        self.dir = dir
        self.mask = pg.mask.from_surface(self.image)
        game.son_epee.play()
        hits = pg.sprite.spritecollide(self, self.game.mobs, False)
        for mob in hits:
            game.son_cris.play()
            mob.lives -= 1
            mob.hurt = pg.time.get_ticks()

    def update(self):
        if self.dir == 'r':
            self.rect.midleft = (self.game.player.rect.midright[0] - 20,self.game.player.rect.midright[1] + 22)
        if self.dir == 'l':
            self.rect.midright = (self.game.player.rect.midleft[0] + 20, self.game.player.rect.midright[1] + 22)

        if pg.time.get_ticks() - self.game.player.hitting > 100:
            self.kill()
            self.game.player.hitting = False

class Gun(pg.sprite.Sprite):
    def __init__(self, game, coord, dir):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.gun_img
        self.rect = self.image.get_rect()
        if dir == 'r':
            self.rect.midleft = coord
        if dir == 'l':
            self.rect.midright = coord
            self.image = pg.transform.flip(self.image, True, False)
        self.dir = dir
    def update(self):
        if self.dir == 'r':
            self.rect.midleft = (self.game.player.rect.midright[0] - 35,self.game.player.rect.midright[1] + 16)
        if self.dir == 'l':
            self.rect.midright = (self.game.player.rect.midleft[0] + 35, self.game.player.rect.midright[1] + 16)
        if pg.time.get_ticks() - self.game.player.shooting > 100:
            self.kill()
            self.game.player.shooting = False

class Bullet(pg.sprite.Sprite):
    def  __init__(self, game, coord, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(0, 553, 19, 14)
        self.rect = self.image.get_rect()
        if dir == 'r':
            self.rect.midleft = coord
            self.velx = BULLET_VEL
        if dir == 'l':
            self.rect.midright = coord
            self.velx = -BULLET_VEL
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.velx
        if pg.sprite.spritecollideany(self, self.game.obstacles):
            self.kill()
        if self.rect.left < 0 or self.rect.right > self.game.mapwidth*TILESIZE or self.rect.x > self.game.camera.offsetx:
            self.kill()

class Bomb(pg.sprite.Sprite):
    def __init__(self, game, coord, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(432, 432, 70, 70)
        self.rect = self.image.get_rect()
        self.blown = False
        if dir == 'r':
            self.rect.midleft = coord
            self.vel = vec(10, -8)
        if dir == 'l':
            self.rect.midright = coord
            self.vel = vec(-10, -8)
        self.countdown = 8

    def update(self):
        if not self.blown:
            self.acc = (0, GRAVITY/ 1.5)
            self.vel += self.acc
            self.rect.x += self.vel.x
            self.rect.y += self.vel.y
            self.boom = pg.time.get_ticks()
            if pg.sprite.spritecollideany(self, self.game.obstacles) or pg.sprite.spritecollideany(self, self.game.platforms):
                self.image = self.game.items_spritesheet.get_image(432, 360, 70, 70)
                self.blown = True
        if self.blown:
            self.explode()

    def explode(self):
        #now = pg.time.get_ticks()
        self.countdown -= 1
        center = self.rect.center
        self.image = pg.transform.scale(self.image, (self.rect[2] + 40, self.rect[3] + 40))
        self.rect = self.image.get_rect()
        self.rect.center = center
        #if now - self.boom == 10:
        if self.countdown == 0:
            self.kill()

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, width, height)
        self.x = self.rect.x = x
        self.y = self.rect.y = y

class Temporary_obs(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.obstacles, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((width, height))
        image = game.tiles_spritesheet.get_image(648, 648, 70, 70)
        for i in range(int(width/TILESIZE)):
            self.image.blit(image,(i*TILESIZE, 0))
        self.rect = self.image.get_rect()
        self.x = x
        self.rect.x = x
        self.y = y
        self.rect.y = y
        self.last_update = 0
        self.render = True

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 6000:
            if self.render :
                self.render = not self.render
                self.last_update = now
                self.rect.x = 0
                self.rect.y = 0
            elif not self.render :
                self.render = not self.render
                self.last_update = now
                self.rect.x = self.x
                self.rect.y = self.y

class Fake_wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, tag):
        self.tag = tag.split(',')
        if self.tag[1] == '1':
            self.groups = game.fake_walls_1
        if self.tag[1] == '2':
            self.groups = game.fake_walls_2
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = self.game.fake_walls_img[self.tag[0]]
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            if self.tag[1] == '1':
                self.game.render_fake_walls_1 = False
            if self.tag[1] == '2':
                self.game.render_fake_walls_2 = False

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, width, height)
        self.x = self.rect.x = x
        self.y = self.rect.y = y

class Moving_platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, coords):
        self._layer = PLATFORMS_LAYER
        self.groups = game.platforms, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        coord = coords.split(',')
        self.image = pg.Surface((width, height))
        if coord[4] == 'grass':
            image = game.tiles_spritesheet.get_image(576,288, 70, 40)
        if coord[4] == 'castle':
            image = game.tiles_spritesheet.get_image(648, 648, 70, 40)
        if coord[4] == 'sand':
            image = game.builds_alt.get_image(70,70, 70, 40)
        for i in range(int(width/TILESIZE)):
            self.image.blit(image,(i*TILESIZE, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.turn = False
        self.pos = vec(x,y)
        self.dir = coord[0]
        self.vel = int(coord[1])
        path = coord[2].split(';')
        self.path = (int(path[0]),int(path[1]))
        self.idle_time = int(coord[3])
        self.last_seen = False

    def update(self):
        if not self.turn:
            self.rect.top -= abs(self.vel)
            hits = pg.sprite.collide_rect(self, self.game.player)
            self.rect.top += abs(self.vel)

            if hits or self.last_seen:
                self.last_seen = hits
                if self.dir == 'x':
                    self.game.player.pos.x += self.vel
                    self.game.player.rect.x += self.vel
                if self.dir == 'y':
                    self.game.player.pos.y += self.vel
                    self.game.player.rect.y += self.vel


            if self.dir == 'x':
                self.rect.x += self.vel
            if self.dir == 'y':
                self.rect.y += self.vel
                #if self.vel < 0:
                #    self.game.player.wall_collide(self, 'y',True)

            self.limits_collide(self.dir)
        else:
            if pg.time.get_ticks() - self.active > 1500:
                self.turn = False
                self.vel *= -1

    def limits_collide(self, dir):
        if dir == 'x':
            if self.rect.right > self.path[1] * TILESIZE :
                self.turn = True
            if self.rect.left < self.path[0] * TILESIZE:
                self.turn = True

        if dir == 'y':
            if self.rect.bottom > self.path[1] * TILESIZE :
                self.turn = True
            if self.rect.top < self.path[0] * TILESIZE:
                self.turn = True
        self.active = pg.time.get_ticks()


    def idle(self):
        self.vel *= -1

class Fragile(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.obstacles, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.tiles_spritesheet.get_image(0, 216, 70, 70)
        self.rect = self.image.get_rect()
        self.x = x
        self.rect.x = x
        self.y = y
        self.rect.y = y
        self.last_update = 0
        self.render = True
        self.state = 'active'

    def update(self):
        now = pg.time.get_ticks()
        if self.state== 'active':
            self.rect.top -= 1
            hits = pg.sprite.collide_rect(self, self.game.player)
            self.rect.top += 1
            if hits:
                self.state = 'fragile'
                self.image = self.game.tiles_spritesheet.get_image(0, 288, 70, 70)
                self.destroy_time = now

        elif self.state == 'fragile':
            if now - self.destroy_time > 1600:
                self.state = 'destroyed'
                self.render = False
                self.rect.x = 0
                self.rect.y = 0
                self.destroy_time = now

        elif self.state == 'destroyed':
            if now - self.destroy_time > 5000:
                self.state = 'active'
                self.render = True
                self.rect.x = self.x
                self.rect.y = self.y
                self.image = self.game.tiles_spritesheet.get_image(0, 216, 70, 70)

class Ladder(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self._layer = PLATFORMS_LAYER
        self.groups = game.ladders, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.tiles_spritesheet.get_image(504, 144, 70, 70)
        self.rect = self.image.get_rect()#pg.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y

class Coin_block(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.coinblock
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.opened = False

    def update(self):
        self.rect.bottom +=1
        hits = pg.sprite.collide_rect(self, self.game.player)
        self.rect.bottom -=1
        if hits:
            self.image = self.game.coinblock_open
            #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
            if not self.opened :
                Coin(self.game, self.x + 18, self.y-TILESIZE + 18, self.width / 2, self.height /2)
                self.opened = True

class Powerup_block(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.itemblock
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.opened = False

    def update(self):
        self.rect.bottom +=1
        hits = pg.sprite.collide_rect(self, self.game.player)
        self.rect.bottom -=1
        if hits:
            self.image = self.game.itemblock_open
            #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
            if not self.opened :
                Powerup(self.game, self.x + 18, self.y-TILESIZE + 18, self.width / 2, self.height /2)
                self.opened = True

class Powerup(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(162, 236, 35, 35)
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        hits = pg.sprite.collide_rect(self,self.game.player)
        if hits:
            self.game.son_gem.play()
            self.game.gem_count += 1
            self.game.score += 300
            self.kill()

class Star(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, tag):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(149, 90, 35, 35)
        self.image = pg.transform.scale(self.image, (55,55))
        self.rect = self.image.get_rect()
        self.rect.x = x - 10
        self.rect.y = y - 10
        self.tag = tag

    def update(self):
        hits = pg.sprite.collide_rect(self,self.game.player)
        if hits:
            if self.tag == '1':
                self.game.stars[0] = True
            if self.tag == '2':
                self.game.stars[1] = True
            if self.tag == '3':
                self.game.stars[2] = True
            self.game.son_gem.play()
            self.game.score += 500
            self.kill()

class Coin(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, flying=True):
        self.groups = game.all_sprites, game.coins
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(306, 378, 35, 35)
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.flying = flying
        if not self.flying:
            self.vel = vec(rd.randint(-4,4),rd.randint(-15,-10))

    def update(self):
        if not self.flying:
            self.vel.y += GRAVITY
            self.rect.centerx += self.vel.x
            hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
            if hits:
                if self.vel.x > 0:
                    self.rect.right = hits[0].rect.left
                if self.vel.x < 0:
                    self.rect.left = hits[0].rect.right
                self.vel.x *= -1
            self.rect.centery += self.vel.y
            hits = pg.sprite.spritecollide(self, self.game.obstacles, False) + pg.sprite.spritecollide(self, self.game.platforms, False)
            if hits:
                if self.vel.y < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.vel.y = 0
                if self.vel.y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.flying = True

        hits = pg.sprite.collide_rect(self,self.game.player)
        if hits:
            self.game.son_coin.play()
            self.game.coin_count += 1
            self.game.score += 100
            self.kill()

class Life(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.heart_full
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        hits = pg.sprite.collide_rect(self,self.game.player)
        if hits:
            self.game.son_gem.play()
            self.game.player.lives += 1
            self.game.score += 400
            self.kill()

class Key(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, tag):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.keys_img[tag]
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tag = tag

    def update(self):
        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            self.game.keys[self.tag] = True
            self.game.son_gem.play()
            self.game.score += 150
            self.kill()

class Locker(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, tag):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.lockers_img[tag]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tag = tag

    def update(self):
        if self.game.keys[self.tag]:
            self.kill()

class Slime(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, index):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #Animation
        self.walking_frames_l = [game.mob_spritesheet.get_image(528, 278, 49, 34),
                                game.mob_spritesheet.get_image(258, 335, 57, 30)]
        self.walking_frames_r = []
        for i in range(2):
            self.walking_frames_r.append(pg.transform.flip(self.walking_frames_l[i], True, False))

        self.hurt_frame_l = game.mob_spritesheet.get_image(477, 457, 49, 34)
        self.hurt_frame_r = pg.transform.flip(self.hurt_frame_l, True, False)
        self.dead_frame = game.mob_spritesheet.get_image(373, 0, 49, 34)
        self.current_frame = 0
        self.image = self.walking_frames_l[0]
        #self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        index = index.split(',')
        self.limit_l = int(index[0]) * TILESIZE
        self.limit_r = int(index[1]) * TILESIZE
        self.pos = vec(self.rect.centerx, self.rect.bottom)
        self.velx = SLIME_VEL
        self.lives = 3
        self.last_update = 0
        self.hurt = 0

    def animate(self):
        if self.velx < 0:
            self.side = 'left'
        elif self.velx > 0:
            self.side = 'right'
        bottom = self.rect.bottom
        now = pg.time.get_ticks()
        # walking animation
        if now - self.hurt < BLINK_TIME:
            if self.side == 'left':
                self.image = self.hurt_frame_l
            if self.side == 'right':
                self.image = self.hurt_frame_r
            self.last_update = 400
        else:
            if now - self.last_update > 400:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                if self.side == 'right':
                    self.image = self.walking_frames_r[self.current_frame]
                elif self.side == 'left':
                    self.image = self.walking_frames_l[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom

    def update(self):
        if self.rect.left < self.limit_l:
            self.rect.left = self.limit_l
            self.pos = vec(self.rect.centerx, self.rect.bottom)
            self.image = pg.transform.flip(self.image, True, False)
            self.velx *= -1
        elif self.rect.right > self.limit_r:
            self.rect.right = self.limit_r
            self.pos = vec(self.rect.centerx, self.rect.bottom)
            self.image = pg.transform.flip(self.image, True, False)
            self.velx *= -1
        self.animate()
        self.rect.midbottom = self.pos
        #self.rect.x += self.velx
        self.pos.x += self.velx
        self.mask = pg.mask.from_surface(self.image)

        if self.lives == 0:
            for i in range(rd.choice([1,1,1,1,1,2,2,2,3,3])):
                Coin(self.game, self.rect.centerx, self.rect.top-10,
                    TILESIZE/2,TILESIZE/2, False)
            self.game.score += 200
            self.kill()

class Fish(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #Animation
        self.upward_frame = game.mob_spritesheet.get_image(529, 60, 45, 60)
        self.downward_frame = game.mob_spritesheet.get_image(529, 0, 45, 60)
        self.hurt_frame_up = game.mob_spritesheet.get_image(573, 346, 45, 60)
        self.hurt_frame_down = pg.transform.flip(self.hurt_frame_up, False, True)

        self.image = self.upward_frame
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(self.rect.centerx, self.rect.bottom)
        self.vely = FISH_VEL
        self.velx = 0
        self.lives = 3
        self.hurt = 0
        self.waiting = False

    def animate(self):
        if self.vely < 0:
            self.side = 'up'
        elif self.vely > 0:
            self.side = 'down'
        bottom = self.rect.midbottom
        now = pg.time.get_ticks()
        # walking animation
        if now - self.hurt < BLINK_TIME:
            if self.side == 'up':
                self.image = self.hurt_frame_up
            if self.side == 'down':
                self.image = self.hurt_frame_down
        else:
            if self.side == 'up':
                self.image = self.upward_frame
            elif self.side == 'down':
                self.image = self.downward_frame
        self.rect = self.image.get_rect()
        self.rect.midbottom = bottom

    def update(self):
        if not self.waiting:
            self.vely += FISH_GRAV
            self.rect.y += self.vely
            self.animate()
        if self.waiting:
            if pg.time.get_ticks() - self.waiting > WAIT_TIME:
                self.waiting = False
                self.vely = FISH_VEL
        elif self.rect.top > self.game.mapheight * TILESIZE:
            self.waiting = pg.time.get_ticks()

        self.mask = pg.mask.from_surface(self.image)
        if self.lives == 0:
            for i in range(rd.choice([1,1,1,2,2,2,2,3,3,3])):
                Coin(self.game, self.rect.centerx, self.rect.top-10,
                    TILESIZE/2,TILESIZE/2, False)
            self.game.score += 350
            self.kill()

class Lavaball(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, tag):
        self.groups = game.all_sprites, game.traps
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #Animation
        self.image = game.items_spritesheet.get_image(23, 458, 24, 24)
        self.frames = []
        for i in range(4):
            image = pg.transform.rotate(self.image, 90*i)
            self.frames.append(image)
        self.current_frame = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(self.rect.centerx, self.rect.bottom)
        self.vely = LAVABALL_VEL
        self.velx = 0
        self.ground = int(tag)
        self.waiting = False
        self.last_update = 0

    def update(self):
        if not self.waiting:
            self.vely += FISH_GRAV
            self.rect.y += self.vely
            self.animate()
        if self.waiting:
            if pg.time.get_ticks() - self.waiting > WAIT_TIME:
                self.waiting = False
                self.vely = LAVABALL_VEL
                self.render = True
        elif self.rect.top > self.ground * TILESIZE:
            self.render = False
            self.waiting = pg.time.get_ticks()

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

class Idle_Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.lives = 5

        self.distance = 0
        self.velx = 0
        self.root = self.rect.centerx
        self.last_move = 0

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move > rd.randint(1200,100000):
            self.last_move = now
            self.velx = rd.randint(2,4)
            var = rd.randint(-TILESIZE*3, TILESIZE*3)
            self.distance = (self.rect.centerx - self.root) #// 20
            if var < self.distance :
                self.velx *= -1
                self.image = pg.transform.flip(self.image, True, False)
        if now - self.last_move < 500:
            self.rect.x += self.velx

class Lava(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.lava
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, width, height)
        self.x = self.rect.x = x
        self.y = self.rect.y = y

    def update(self):
        hits = pg.sprite.collide_rect(self,self.game.player)
        if hits:
            self.game.player.lives = 0

class Spike(pg.sprite.Sprite):
    def  __init__(self, game, x, y, width, height, time = None):
        self.groups = game.traps, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(347, 35, 70, 35)
        self.rect = self.image.get_rect()
        self.velx = 0
        self.x = x
        self.rect.x = x
        self.y = y
        self.rect.y = y
        if time:
            Time = time.split(',')
            self.time_active = int(Time[0])
            self.time_passive = int(Time[1])
            self.last_update = 0
            self.render = True

    def update(self):
        try:
            now = pg.time.get_ticks()
            if self.render:
                if now - self.last_update > self.time_active:
                    self.render = False
                    self.last_update = now
                    self.rect.x = 0
                    self.rect.y = 0
            elif not self.render:
                if now - self.last_update > self.time_passive:
                    self.render = True
                    self.last_update = now
                    self.rect.x = self.x
                    self.rect.y = self.y
        except:pass

class Launcher(pg.sprite.Sprite):
    def  __init__(self, game, x, y, width, height, tag):
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y
        self.last_update = 0
        tag = tag.split(',')
        self.dir = tag[0]
        self.time = int(tag[1])
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.time:
            self.last_update = now
            if self.dir == 'r':
                Fireball(self.game, (self.rect.midright[0],self.rect.midright[1]), 'r')
            if self.dir == 'l':
                Fireball(self.game, (self.rect.midleft[0], self.rect.midright[1]), 'l')

class Fireball(pg.sprite.Sprite):
    def  __init__(self, game, coord, dir):
        self.groups = game.all_sprites, game.traps
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(23, 458, 24, 24)
        self.frames = []
        for i in range(4):
            image = pg.transform.rotate(self.image, 90*i)
            self.frames.append(image)
        self.rect = self.image.get_rect()
        if dir == 'r':
            self.rect.midleft = coord
            self.velx = FIREBALL_SPEED
        if dir == 'l':
            self.rect.midright = coord
            self.velx = -FIREBALL_SPEED
        self.mask = pg.mask.from_surface(self.image)
        self.last_update = 0
        self.current_frame = 0
        self.wait = 0

    def update(self):
        if not self.wait:
            self.rect.x += self.velx
            now = pg.time.get_ticks()
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

            if pg.sprite.spritecollideany(self, self.game.obstacles):
                self.kill()
            if self.rect.left < 0 or self.rect.right > self.game.mapwidth*TILESIZE:
                self.kill()
            if pg.sprite.collide_rect(self, self.game.player):
                self.wait = pg.time.get_ticks()
        else:
            if pg.time.get_ticks() - self.wait > 3:
                self.kill()

class Button(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, tag):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(288, 504, 70, 70)
        #self.image = pg.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = width
        self.height = height
        self.tag = tag

    def update(self):
        self.rect.top -=1
        hits = pg.sprite.collide_rect(self, self.game.player)
        self.rect.top +=1
        if hits:
            if self.tag == '1':
                #self.image = self.game.items_spritesheet.get_image(419, 72, 70, 70)
                #self.image = pg.transform.scale(self.image, (self.width, self.height))
                for i in range(4):
                    Ladder(self.game, 7 * TILESIZE, (10+i) * TILESIZE, TILESIZE, TILESIZE)
                Springboard(self.game, 60 * TILESIZE, 17 * TILESIZE, TILESIZE, TILESIZE)
            if self.tag == '2':
                for i in range(4):
                    Ladder(self.game, 45 * TILESIZE, (15+i) * TILESIZE, TILESIZE, TILESIZE)
            self.kill()

class Springboard(pg.sprite.Sprite):
    def __init__(self, game, x, y, height, width):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.items_spritesheet.get_image(432, 288, 70, 70)
        #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.updated = 0

    def update(self):
        self.rect.top -=1
        hits = pg.sprite.collide_rect(self, self.game.player)
        self.rect.top +=1
        if hits:
            self.game.player.vel.y = -30 * TILESIZE/48
            self.image = self.game.items_spritesheet.get_image(432, 216, 70, 70)
            #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
            self.updated = pg.time.get_ticks()
        if self.updated > 0:
            if pg.time.get_ticks() - self.updated > 200:
                self.image = self.game.items_spritesheet.get_image(432, 288, 70, 70)
                #self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
                self.updated = 0

class End(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.rect = pg.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y
    def update(self):
        if pg.sprite.collide_rect(self, self.game.player):
            self.game.win = True
            self.game.playing = False
