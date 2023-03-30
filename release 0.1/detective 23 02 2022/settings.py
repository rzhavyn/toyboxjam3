import pygame
Vector2 = pygame.math.Vector2

class app:
    CAPTION =              'toybox_detective'
    VERSION =              '0.1'

    FPS =                  30.0

    DISP_FLAGS =           0
    DISP_DEPTH =           0

    TS =                   8

    # Screen size (128, 136)
    DISP_W =               TS*16
    DISP_H =               TS*17

    END_WIN_W =            DISP_W*4 # 512
    END_WIN_H =            DISP_H*4 # 544

IKIT_ZERO = {'upper':0,'lower':0,'hair':0,'facial_hair':0}

ground_level = 6*app.TS

player_locs = {
    'BossBriefroom': {     'start_game': Vector2(11*app.TS, ground_level),
                           'from_Corridor': Vector2(16*app.TS, ground_level)},

    'Corridor': {          'from_BossBriefroom': Vector2(-app.TS, ground_level),
                           'from_Archive': Vector2(4*app.TS, ground_level),
                           'from_Jail': Vector2(8*app.TS, ground_level), # 7
                           'from_Office': Vector2(12*app.TS, ground_level),
                           'from_Entrance': Vector2(16*app.TS, ground_level)},

    'Jail': {              'from_Corridor': Vector2(8*app.TS, ground_level)},

    'Archive': {           'from_Corridor': Vector2(-app.TS, ground_level)},

    'Office': {            'from_Corridor': Vector2(-app.TS, ground_level)},

    'Entrance': {          'from_Corridor': Vector2(-app.TS, ground_level),
                           'from_Start': Vector2(16*app.TS, ground_level)}

    }

pico_white = pygame.Color('#fff1e8')
pico_light_gray = pygame.Color('#c2c3c7')
pico_dark_gray = pygame.Color('#5f574f')
