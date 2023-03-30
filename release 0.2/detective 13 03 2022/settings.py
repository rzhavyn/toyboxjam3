import pygame
Vector2 = pygame.math.Vector2

class app:
    CAPTION =              'Toybox Detective'
    VERSION =              '0.2'
    AUTHOR =               'rzhavyn'

    FPS =                  30.0
    TS =                   8

    # Screen size (128, 136)
    DISP_W =               TS*16
    DISP_H =               TS*17

    # (512, 544)
    END_WIN_W =            DISP_W*4
    END_WIN_H =            DISP_H*4

DEBUG = False

IKIT_ZERO = {'upper':0,'lower':0,'hair':0,'facial_hair':0}

ground = 6*app.TS

player_locs = {
    'BossBriefroom': {     'start_game': Vector2(11*app.TS, ground),
                           'from_Corridor': Vector2(16*app.TS, ground)},

    'Corridor': {          'from_BossBriefroom': Vector2(-app.TS, ground),
                           'from_Archive': Vector2(4*app.TS, ground),
                           'from_Jail': Vector2(8*app.TS, ground),
                           'from_Office': Vector2(12*app.TS, ground),
                           'from_Entrance': Vector2(16*app.TS, ground)},

    'Jail': {              'from_Corridor': Vector2(8*app.TS, ground)},

    'Archive': {           'from_Corridor': Vector2(-app.TS, ground)},

    'Office': {            'from_Corridor': Vector2(-app.TS, ground)},

    'Entrance': {          'from_Corridor': Vector2(-app.TS, ground),
                           'from_Start': Vector2(16*app.TS, ground)}

    }

pico_white = pygame.Color('#fff1e8')
pico_light_gray = pygame.Color('#c2c3c7')
pico_dark_gray = pygame.Color('#5f574f')
pico_green = pygame.Color('#00e436')
pico_dark_green = pygame.Color('#008751')
pico_cyan = pygame.Color('#29adff')
pico_dark_magenta = pygame.Color('#7e2553')
pico_red = pygame.Color('#ff004d')
pico_yellow = pygame.Color('#ffec27')
