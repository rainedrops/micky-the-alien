import pygame as pg


#Game values
TITLE = "Platformer level One"
FPS = 60
#Level Propreties
TILESIZE = 70
cste = 1
#Windowsize
camwidth = 35
camheight = 15

#Level info are located in function

WIDTH = 1920#camwidth * TILESIZE
HEIGHT = 1080#camheight * TILESIZE

#colors (R, G, B)
bg = (30,144,255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
DARKWHITE = (200, 200, 200)
green = (0, 120, 0)
GREEN = (0, 155, 50)
dark_red = (105, 0, 0)
red = (200, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
ORANGE = (255,140,0)
PURPLE = (128,0,128)
LIGHTBLUE = (176,224,230)

P_W = int(44 * 3/2)
P_H = int(68 * 3/2)
GRAVITY = 1 * 3/2
P_JUMP = -20 * 3/2
P_ACC = 1.1 * 3/2
P_FRIC = -.2 #* 3/2
P_KB = -36 * 3/2

DAMAGE_ALPHA = [i for i in range(0,255,20)]

BULLET_VEL = 12 * 3/2

PLAYER_RADIUS = 128 * 3/2
#Mob Patterns
SLIME_VEL = -2 * 3/2
FISH_VEL = -25
LAVABALL_VEL = -25
FISH_GRAV = .6
WAIT_TIME = 2000
BLINK_TIME = 80
FIREBALL_SPEED = 6
#Layers
PLAYER_LAYER = 2
PLATFORMS_LAYER = 1
