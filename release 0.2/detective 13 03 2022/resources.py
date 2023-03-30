import copy
import random
import os
import sys

import pygame
from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer

import settings
import text_mono

TS = settings.app.TS
Vector2 = pygame.math.Vector2


def load():
    return LoadAssets()


def resource_path(relative_path):
    ''' Get absolute path to resource, works for dev and for PyInstaller
        https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/44352931#44352931
    '''
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def split_spritesheet(filename, size, cols, rows, colorkey = None, scaleimg = None, alpha = False):
    '''
    size: (w, h) int, ширина и высота каждой картинки (ячейки)
    cols, rows: int, количество ячеек в спрайтшите вертикально и горизонтально
    colorkey: если не None, то у всех загруженных картинок бит прозрачности будет равен colorkey
    scaleimg: если не None, то каждая картинка будет увеличена в scaleimg (целое) раз
    '''

    try:
        if alpha:
            sheet = pygame.image.load(filename).convert_alpha()
        else:
            sheet = pygame.image.load(filename).convert()

    except pygame.error as message:
        raise SystemExit(message)

    subsurfaces = {}
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect((x*size[0], y*size[1]), size)
            tile = sheet.subsurface(rect)

            if colorkey is not None:
                tile.set_colorkey(colorkey)

            if scaleimg is not None:
                tile = pygame.transform.scale(tile, (size[0]*scaleimg, size[1]*scaleimg))

            subsurfaces[int(x+y*cols)] = tile

    return subsurfaces # {0: surface, 1: surface, ...}


class LoadAssets(object):
    def __init__(self):
        # шрифт, основные детали фотороботов, детали графики объектов, нпс
        sheet1 = split_spritesheet(resource_path('assets/democart.png'), (TS, TS), 16, 16)
        # игрок и его анимации
        sheet2 = split_spritesheet(resource_path('assets/neato_16_8.png'), (TS, TS), 16, 16)
        # детали графики уровня, яблоко, сердце
        sheet3 = split_spritesheet(resource_path('assets/tbj2_startcart2spr.png'), (TS, TS), 16, 16)
        # курица, жук, человечек, улитка
        sheet4 = split_spritesheet(resource_path('assets/add_sprites.png'), (TS, TS), 16, 16)
        # символы PICO-8
        sheet5 = split_spritesheet(resource_path('assets/pico8_symbols.png'), (TS, TS), 16, 2, pygame.Color('black'))

        # Иконки зацепок
        self.clues_icons = {'sword':None,'pickaxe':None,'hammer':None,'chest':None,
                            'g_key':None,'s_key':None,'bottle':None,'r_heart':None,
                            'gun':None,'goblet':None,'gem':None,'grave':None,
                            'bell':None,'pike':None,'skull':None,'bubble':None,
                            'leaf':None,'coin':None,'o_lock':None,'g_apple':None,
                            'g_heart':None}
        for num_key in list(sheet1.keys()):
            if num_key == 26:
                self.clues_icons['sword'] = sheet1[num_key].copy()
            if num_key == 27:
                self.clues_icons['pickaxe'] = sheet1[num_key].copy()
            if num_key == 28:
                self.clues_icons['hammer'] = sheet1[num_key].copy()
            if num_key == 45:
                self.clues_icons['chest'] = sheet1[num_key].copy()
            if num_key == 30:
                self.clues_icons['g_key'] = sheet1[num_key].copy()
            if num_key == 31:
                self.clues_icons['s_key'] = sheet1[num_key].copy()
            if num_key == 65:
                self.clues_icons['bottle'] = sheet1[num_key].copy()
            if num_key == 64:
                self.clues_icons['r_heart'] = sheet1[num_key].copy()
            if num_key == 79:
                self.clues_icons['gun'] = sheet1[num_key].copy()
            if num_key == 75:
                self.clues_icons['goblet'] = sheet1[num_key].copy()
            if num_key == 122:
                self.clues_icons['gem'] = sheet1[num_key].copy()
            if num_key == 52:
                self.clues_icons['grave'] = sheet1[num_key].copy()
            if num_key == 56:
                self.clues_icons['bell'] = sheet1[num_key].copy()
            if num_key == 47:
                self.clues_icons['pike'] = sheet1[num_key].copy()
            if num_key == 117:
                self.clues_icons['skull'] = sheet1[num_key].copy()
            if num_key == 108:
                self.clues_icons['bubble'] = sheet1[num_key].copy()
            if num_key == 107:
                self.clues_icons['leaf'] = sheet1[num_key].copy()
            if num_key == 66:
                self.clues_icons['coin'] = sheet1[num_key].copy()
            if num_key == 139:
                self.clues_icons['o_lock'] = sheet1[num_key].copy()
        for num_key in list(sheet3.keys()):
            if num_key == 105:
                self.clues_icons['g_apple'] = sheet3[num_key].copy()
            if num_key == 110:
                self.clues_icons['g_heart'] = sheet3[num_key].copy()

        self.pico8_symbols = {'whole':sheet5[0],'whole_dots':sheet5[1],'mask':sheet5[2],'down':sheet5[3],
                              'dots':sheet5[4],'suriken':sheet5[5],'ball':sheet5[6],'heart':sheet5[7],
                              'eye':sheet5[8],'man':sheet5[9],'house':sheet5[10],'left':sheet5[11],
                              'face':sheet5[12],'note':sheet5[13],'o':sheet5[14],'star':sheet5[15],
                              'line_dots':sheet5[16],'right':sheet5[17],'starship':sheet5[18],
                              'sand_clock':sheet5[19],'up':sheet5[20],'birds':sheet5[21],'monutain':sheet5[22],
                              'x':sheet5[23],'lines_hor':sheet5[24],'lines_vert':sheet5[25]}

        # Тайловый шрифт
        # цифры/буквы/знаки (sheet1 192 - 255)
        font_tiles = {}
        n = 0
        for num_key in list(sheet1.keys()):
            if 192 <= num_key <= 255:
                font_tiles[n] = sheet1[num_key].copy()
                n += 1
        # тайлы зацепок (21 шт, буквы a - u)
        for item in self.clues_icons.items():
            font_tiles[n] = item[1].copy()
            n += 1
        # символы PICO8 (26 шт, символы юникода 00C0 - 00D9)
        for item in self.pico8_symbols.items():
            font_tiles[n] = item[1].copy()
            n += 1

        self.tile_font = text_mono.generate_font(font_tiles)


        # Загрузить комнаты в формате Tiled с помощью pytmx
        self.boss_tmx = load_pygame(resource_path('assets/boss.tmx'))
        self.corridor_tmx = load_pygame(resource_path('assets/corridor.tmx'))
        self.archive_tmx = load_pygame(resource_path('assets/archive.tmx'))
        self.jail_tmx = load_pygame(resource_path('assets/jail.tmx'))
        self.office_tmx = load_pygame(resource_path('assets/office.tmx'))
        self.entrance_tmx = load_pygame(resource_path('assets/entrance.tmx'))
        # Загрузить фоны экранов
        self.searchinarch_tmx = load_pygame(resource_path('assets/searchinarchive.tmx'))
        self.playercomp_ikit_tmx = load_pygame(resource_path('assets/playercomp_ikit.tmx'))
        self.playercomp_todo_tmx = load_pygame(resource_path('assets/playercomp_todo.tmx'))
        self.interrogation_tmx = load_pygame(resource_path('assets/interrogation.tmx'))
        self.start_tmx = load_pygame(resource_path('assets/start.tmx'))

        self.splash_tmx = load_pygame(resource_path('assets/splash.tmx'))

        # Загрузить фрагменты лиц
        self.identikit_parts = {'upper': [], 'lower': [], 'hair': [], 'facial_hair': []}
        self.bald_parts = {'hair': [], 'facial_hair': []} # {'hair': [i_p_hair_num, bald_part_img], ...}

        for fname in os.listdir(resource_path('parts')):
            tmx_path = resource_path('parts/'+fname)
            img_type = fname.rstrip('.tmx').rstrip('1234567890')

            if img_type == 'facial_hair':
                # Сделать из TiledMap просто картинку
                tmx = load_pygame(tmx_path)
                tw = tmx.tilewidth
                th = tmx.tileheight

                img = pygame.Surface((tw*TS, th*TS)).convert()
                img.set_colorkey(pygame.Color('magenta'))
                img.fill(pygame.Color('magenta'))
                if len(self.identikit_parts['facial_hair']) == 0: # ! 0 элемент = прозрачая пустая картинка
                    self.identikit_parts['facial_hair'].append(img.copy())

                # Копия пустой картинки, если это BALD
                for prop in list(tmx.properties.keys()):
                    if prop == 'bald':
                        if tmx.properties['bald']:
                            n = int(fname.lstrip('facial_hair').rstrip('.tmx'))
                            self.bald_parts['facial_hair'].append(n)
                            img.fill(pygame.Color('magenta'))
                            self.bald_parts['facial_hair'].append(img.copy())

                for layer in tmx.visible_layers:
                    if isinstance(layer, TiledTileLayer):
                        for x, y, image in layer.tiles():
                            img.blit(image, (x*tw, y*th))
                self.identikit_parts['facial_hair'].append(img.copy())

            elif img_type == 'hair':
                tmx = load_pygame(tmx_path)
                tw = tmx.tilewidth
                th = tmx.tileheight

                img = pygame.Surface((tw*TS, th*TS)).convert()
                img.set_colorkey(pygame.Color('magenta'))
                img.fill(pygame.Color('magenta'))
                if len(self.identikit_parts['hair']) == 0:
                    self.identikit_parts['hair'].append(img.copy())

                # Копия пустой картинки, если это BALD
                for prop in list(tmx.properties.keys()):
                    if prop == 'bald':
                        if tmx.properties['bald']:
                            n = int(fname.lstrip('hair').rstrip('.tmx'))
                            self.bald_parts['hair'].append(n)
                            img.fill(pygame.Color('magenta'))
                            self.bald_parts['hair'].append(img.copy())

                for layer in tmx.visible_layers:
                    if isinstance(layer, TiledTileLayer):
                        for x, y, image in layer.tiles():
                            img.blit(image, (x*tw, y*th))
                self.identikit_parts['hair'].append(img.copy())

            elif img_type == 'lower':
                tmx = load_pygame(tmx_path)
                tw = tmx.tilewidth
                th = tmx.tileheight

                img = pygame.Surface((tw*TS, th*TS)).convert()
                img.set_colorkey(pygame.Color('magenta'))
                img.fill(pygame.Color('magenta'))
                if len(self.identikit_parts['lower']) == 0:
                    self.identikit_parts['lower'].append(img.copy())

                for layer in tmx.visible_layers:
                    if isinstance(layer, TiledTileLayer):
                        for x, y, image in layer.tiles():
                            img.blit(image, (x*tw, y*th))
                self.identikit_parts['lower'].append(img.copy())

            elif img_type == 'upper':
                tmx = load_pygame(tmx_path)
                tw = tmx.tilewidth
                th = tmx.tileheight

                img = pygame.Surface((tw*TS, th*TS)).convert()
                img.set_colorkey(pygame.Color('magenta'))
                img.fill(pygame.Color('magenta'))
                if len(self.identikit_parts['upper']) == 0:
                    self.identikit_parts['upper'].append(img.copy())

                for layer in tmx.visible_layers:
                    if isinstance(layer, TiledTileLayer):
                        for x, y, image in layer.tiles():
                            img.blit(image, (x*tw, y*th))
                self.identikit_parts['upper'].append(img.copy())



        # Очередное дело:
        self.case_main_clues = []
        self.case_main_hints = []
        self.case_false_hints = []
        self.true_criminal = []
        self.true_crim_ip_num = []
        self.false_suspects_parts = {}
        self.archive_cases = []
        self.cheat_image = None


        self.talks = {'boss': {'new_clues':['TODAY WE\'VE GOT A MYSTERIOUS {} BURGLARY IN OUR LOCAL MUSEUM. FIND THAT CRIMINAL, I WANT TO LOOK AT HIS EYES!',
                                            'SOMEONE IN THIS TOWN DID A DISGUSTING ATROCITY. {} HAS BEEN STOLEN IN THE MIDDLE OF BAZZAR!',
                                            'DETECTIVE, GRAND THEFT HAPPENED TONIGHT! HOW DARE THEY?! {} HAS BEEN TAKEN FROM UNDER THE CUSTODY!',
                                            'A LOT OF OUR TOWN\'S BANKS COULD NOT FIND THE {} THIS MORNING. NOW YOU COME INTO PLAY!'],

                               'win':['WELL DONE, SON! YOU\'VE EARNED YOUR BUCKS FOR SHURE. DO YOU WANT TO GO FURTHER?'],

                               'end':['IT IS ENOUGH FOR YOU THIS DAY, DETECTIVE. YOU CANNOT EARN ALL THE BUCKS IN THE WORLD. GO HOME AND REST NOW'],

                               'chat':['DON\'T WORRY, YOU CAN HANDLE IT, SON. IMMIDEATELY',
                                       '\'IT\'S OKAY TO MAKE MISTAKES, DETECTIVE\' I WOULD SAY, BUT INSTEAD I SAY \'GET BACK TO WORK, SON!\'',
                                       'I THOUGHT, I GAVE YOU AN IMPORTANT TASK!',
                                       'WHY ARE YOU STILL HERE?',
                                       'DID YOU HAVE A TASK? GET BACK TO WORK!',
                                       'CAN\'T HELP YOU WITH THIS, BETTER LOOK IN THE ARCHIVES. DON\'T BOTHER ME AGAIN!'],

                               'labels':{'new_clues': ['×YES,SIR', '×GOT IT', '×ACCEPT', '×AGREE'],
                                         'chat': ['×YES,SIR', '×HMMM..', '×YES', '×SORRY'],
                                         'win': ['×YES,SIR']}},

                     'witness': {'add_clue':['I SAW THIS {}{}{} SOMWHERE IN TOWN. MAYBE IT WILL HELP YOU',
                                            'THIS {}{}{} WERE LYING ON THE GROUND NEAR THE CRIME SCENE. YOU MIGHT KNOW WHAT IS THAT',
                                            'TAKE {}{}{} UNDER THE CUSTODY, PLEASE! I\'M TOO SCARED TO HAVE IT AT MY PLACE'],

                                 'chat': ['I ALREADY TOLD YOU ALL THAT I KNOW. LEAVE ME ALONE, PLEASE'],

                                 'labels':{'take':['×TAKE'],
                                           'refuse':['REFUSE'],
                                           'chat': ['×OKAY', '×HMMM..']}},

                    'suspect': {'name': 'SUSPECT',
                                'chat': ['I WILL TELL YOU NOTHING, COP! I HAVE THE RIGHT TO MAKE ONE CALL!',
                                        'YOU WILL PAY FOR THAT, SOONER OR LATER, COP!'],

                                'labels':['×OKAY', '×HMMM..', '×MAYBE', '×SILENCE!']},

                    'janitor':{'name': 'JEREMIAH',
                               'chat': ['PLEASE, DON\'T STEP ON PUDDLES... YOU MAY FALL',
                                        'PLEASE, DON\'T SLAM OUR DOORS. IF YOU BREAK IT, IT WILL HURT YOUR PAY-CHECKS',
                                        'TIME IS ALL THAT MATTERS, AFTER ALL... OH, LUNCH TIME!',
                                        'SOME PEOPLE SAY IF YOU WILL BE TRYING HARD ENOUGH, YOU COULD BEAT ANYTHING. LIARS!',
                                        'KEEP AT GOOD WORK, KID',
                                        'I DON\'T TRUST THAT SUIT-BOY. TOO MUCH SWEET-TALK',
                                        'MAIN TRICK IS TO KEEP LOWEST POSSIBLE AMOUNT OF WATER ON A MOP',
                                        'NO MATTER HOW HARD YOU TRY, IT ALWAYS THE SAME... OH, EXCUSE MY RAMBLINGS',
                                        'YEARS AGO A GUNFIGHT HAPPENED IN THIS STATION. BLOOD IS HARD TO GET RID OFF, YOU KNOW?',
                                        'MUMBLING: <OUR BOSS THINKS THAT HE KNOWS EVERYTHING. THAT STUPID BA-HMPH...> OH, HELLO THERE!',
                                        'THIS WALLS HAVE SEEN A LOT. MAYBE A LITTLE TOO MUCH, ACTUALLY. NEW PAINT MIGHT HELP',
                                        'MUMBLING: <THEY GOT MY NAME WRONG. IT\'S YIRMEYAHU, NOT JEREMIAH-NAH- HMPF...>',
                                        'MUMBLING: <ONE, TWO, THREE, FOUR...? BULLETHOLES ARE VISIBLE AGAIN, CRAP...>'],

                               'labels': ['×OKAY', '×HMMM..', '×YES', '×GOT YA', '×SORRY']},

                   'archivist':{'name': 'JOE',
                               'chat': ['WELL HELLO THERE! MAY I ASK WHAT\'S ON YOUT MIND? I THINK, I CAN HELP',
                                        'PLEASE, ALWAYS PUT EVERYTING BACK TO THEIR PLACES. THANKS',
                                        'I WISH OUR BUDGET CAN AFFORD HIGHER LADDERS',
                                        'COMPUTERS ARE AMAZING AT STORING INFORMATION, BUT PERSONALLY I PREFER REAL PAPER',
                                        'PLEASE, DON\'T USE ANY ILLEAGAL SOFTWARE. I AM TIRED OF CLEANING AFTER YOU, SMART-GUYS',
                                        'MY O MY, THAT\'S A NIIICE LOOKING PICTURE... EH? <ERRATICK CLICKS> HMM. I\'M DOING SOME RESEARCH HERE. WHAT DO YOU NEED?',
                                        'YOU KNOW OUR JANITOR JEREMAIH? HE START WORKING HERE EVEN BEFORE ME. NO, I DON\'T KNOW WHEN HE ENLISTED HERE',
                                        'I DO REMEMBER OUR OL\' BOSS. HE WAS A MAN OF WORD. A BIT TOUGH WITH EMPLOYEES, YES. BUT!',
                                        'NEW BOSS? HECK FOR ME HE IS TOO SOFT, CAN ALLOW YOURSELF A HESITATION. NOT THE BEST TRAITS, IF YOU ASK ME',
                                        'IN THE END, IT ALL COMES TO ARCHIVES, TO HISTORY, RIGHT, KID?',
                                        'I\'M IN CHARGE HERE ALMOST FOR THREE DECADES. I\'M AS GOOD AS THESE NEW THIN COPMUTERS, IF YOU ASK ME',
                                        'EVERYONE LOVES TO TALK A LOT, BUT ABOVE THAT MAIN RULE OF UNIVERSE IS SOLID: HISTORY REPEATS ITSELF',
                                        'TRY TO KEEP YOUR RELATIONS WITH COOWOKERS HIGH. EVERYONE NEEDS A SHOULDER SOMETIMES'],

                               'labels': ['×OKAY', '×HMMM..', '×THANKS', '×YES', '×WELL,OK']},

                   'cop1':{'name': 'TERRY',
                           'chat': ['HOW IS YOUR DAY GOING?',
                                    'TRY NOT TO LISTEN TO OUR LAWYER RAMBLINGS. HE GOT PAID ON EVERY WORD HE SPITS',
                                    'MY COMPUTER SUDDENLY TURNED OFF! DID YOU JUST STEPPED ON THE WIRE?!',
                                    'REMEMBER TO SAVE YOUR PROGRESS TIME TO TIME. SAVES SOME NERVES, YOU KNOW?',
                                    'MAN! THIS SPAM E-MAIL I GOT TODAY IS SOOOO INTERESTING',
                                    'HEY, DID YOU KNOW THAT OUR PLANET IS ACTUALLY FLAT? ME NEITHER', #?
                                    'IF WE LIVE ON A ROUND BALL OF ROCK AND DIRT, WHY WE DON\'T JUST FALL OFF?',
                                    'IT IS CRAZY, BUT ON THE OTHER SIDE OF EARTH WATER SPINS DIFFERENTELY WHEN YOU FLUSH WC',
                                    'HA-HA-HA. LOOK AT THIS. <HE SHOWS YOU A FUNNY LOOKING PICTURE. IT\'S CUTE>',
                                    'IS IT TURTLE OR WHALE? AND WHY NO ONE QUESTIONS ELEPHANTS? BUGGERS',
                                    'IF OUR PLANET SPINS, WHY IF I JUMP I DON\'T FLEW OFF INTO SPACE? GRAVITATION, THE WHAT?',
                                    'WHAT WAS IT? <CLICK CLICK BEEP> DAMN, WRONG ONE',
                                    'TSK. IT-GUY ACCIDENTLY REORDERED MY DESKTOP ICONS, NOW I CAN\'T FIND ANYTHING. THAT EGG-HEAD'],

                           'labels': ['×OKAY', '×HMMM..', '×YES', '×GOT YA', '×YEP', '×CRAZY', '×WHAT']},

                   'cop2':{'name': 'LT.KING',
                           'chat': ['HI! <SHAKES YOUR HAND AND RIGHT AFTER THAT USES AN ANTI-BACTERIA WIPES>',
                                    'I\'M GOING TO GET SOME FOOD AND COFFEE, YOU\'RE IN?',
                                    'TODAY I SAW A NICE LOOKING MUFFINS... YOU KNOW, CAFFETERIA DOWN THE STREET',
                                    'IT\'S BEEN A WHILE WE\'VE GOT OUR BADGES, BUT I\'M STUCK WITH COMPUTER LIKE FOREVER. DAMN PAPERS...',
                                    'DID YOU KNOW, THAT IF YOU DON\'T INVITE A VAMPIRE TO YOUR HOUSE, IT CAN\'DO ANYTHING? HMMM...',
                                    'ZOMBIE VIRUS OR APOCALYPSIS CAN EXIST ONLY IN FANTASIES. IN REAL LIFE THEY ARE... UHMM... UNREAL?',
                                    'IMAGINE IF MAGIC WOULD EXIST IN OUR WORLD. THAT WILL BE A HELL OF PLACE. HUMANS ARE ALWAYS HUMANS',
                                    'I SPENT LAST DAY-OFF WITH MY KID. WE WERE WATCHING EASTERN CARTOONS. IT\'S WEIRD, IF YOU ASK ME',
                                    'MUMBLING: <IT\'S NOT ENOUGH TO TAKE MY PRIDE! YOU HAVE TO TAKE MY LEFE! OH, WELL, YOU GOT ME>',
                                    'YOU KNOW, THIS COMPUTERS ARE NEW, HELL, AND IT\'S EVEN BETTER THAN I HAVE AT HOME. STRANGE',
                                    'EVER WATCHED A SCARY MOVIE? I DON\'T-STUPID UGLY FACES AND ACTORS THAT SUITS THEM',
                                    'IF YOU NEED SOME INFORMATION, YOU CAN ASK JOE. HE LOVES TO TALK ABOUT HISTORY. I DON\'T',
                                    'CAN YOU IMAGINE A PIZZA WITH BANANAS AND PINEAPPLES? NO, THAT\'S NOT A FRUIT PIE! PIZZA!'],

                           'labels': ['×OKAY', '×HMMM..', '×YES', '×GOT YA', '×YEP', '×CRAZY', '×WHAT']},

                   'lawyer':{'name': 'MR.TYLER',
                            'chat': ['HI! <HE IS WATCHING THROUGH YOU, IT LOOKS LIKE MANY THOUGHTS WHIRLING IN HIS HEAD>',
                                     'GOOD MORNING! LET\'S WORK TODAY AS BEST AS WE CAN!',
                                     'IF YOU WANT I CAN GRAB YOU A CUP OF COFFEE',
                                     'MATTHEW AND TERRY ARE GRATE GUYS, BUT A LITTE GRIM',
                                     'OUR JANITOR IS DOING AMAZING JOB HERE! FLOOR IS SO SMOOTH AND CLEAN THAT I ALMOST FALL ONCE! HA-HA!',
                                     'YOUR BOSS IS A BIT SHORT FUSED BUT OVERALL NOT THAT BAD. I\'VE SEEN WORSE...',
                                     'WE SHOULD KEEP OURSELFS POSITIVE. IT HELPS WITH BRAINWORK A LOT. IT\'S ALSO SIMPLE - JUST TRY TO SMILE :)',
                                     'EVERYONE HERE LOOKS AT ME WITH DISGUST. I UNDERSTAND WHY, AND DON\'T ANGRY AT THEM',
                                     'IF WE GET WRONG SUSPECT CHARGED IT CAN EASILY RUIN HIS LIFE. BUREAUCRACY IS MERCYLESS',
                                     'MY DAD WAS CHARGED FOR TEN YEARS. HE WAS INNOCENT. GOVERNMENT PAID HIM A LITTLE AS EXCUSE',
                                     'I\'M NOT TRYING TO COVER MY CLIENTS. I WANT TO FIND TRUTH AS MUCH AS YOU DO',
                                     'SOMETIMES PEOPLE UNDER STRESS CAN SAY SOMETHING, THAT GRAVE THEM INSTANTLY, EVEN IF THEY ARE INNOCENT',
                                     'I WISH SOME DAY LAW WILL BE HANDLED BY COLD BLOODED ROBOT THAT WILL MAKE DECISIONS BASED ON FACTS AND NOTHING ELSE MORE'],

                            'labels': ['×OKAY', '×HMMM..', '×YES']},


                   'dutyofficer':{'name': 'ROB',
                                  'start_scene': ['BOSS HAS BEEN LOOKING FOR YOU, DETECTIVE'],
                                  'send_target': ['LET\'S SEE, WHAT WE HAVE HERE. UHM, SUCH PRETTY FACE... CAN I SEND OUT IT, DETECTIVE?',
                                                  'WHERE DID YOU FIND THIS SCARY FACE? IT IS OUR SUSPECT, EH? I\'LL SEND IT OUT IMMEDIATELY'],

                                  'not_finalized': ['NO, YOU SHOULD FINALIZE SUSPECT IDENTIKIT FIRST'],

                                  'chat':['HEY, YOU! FOR WHAT PURPOSE DID YOU CO... A, HELLO, DETECTIVE',
                                          'ANOTHER DAY, ANOTHER WORK, EH?',
                                          'TODAY IS MY DUTY DAY, IN FACT I\'M HERE MOST OF THE TIME. DAMN SCHEDULES',
                                          'YOU LOOK A BIT PALE, IS EVERYTHING ALRIGHT?',
                                          'YESTERDAY I GOT ANNOYING VISITOR. OLD HAG TRIED TO GET INTO ARCHIVES, AND SHE STOLE MY PEN!',
                                          'MUMBLING: <RIGHT... ASK NAME AND WHAT THEY WANT TO DO... DON\'T GET ANGRY... THEY DON\'T DESERVE IT...>',
                                          'MUMBLING: <CAN I GET THIS GUN FROM UNDER THE DESK FAST ENOUGH?> EH? OH, HI!',
                                          'YOU KNOW WHAT IS UNFAIR? I CAN\'T LOWER THE IRON SHUTS ON ENTERANCE. ONLY BOSS CAN DO IT, FROM HIS OFFICE',
                                          'I MAY SOUND A BIT PARANOID, BUT KNOW WHAT? I WAS HIRED AFTER THE GUY WHO WAS NOT SO PARANOID',
                                          'DON\'T FORGET TO ATTEND AT SHOOTING RANGE. DON\'T GET RUSTY. IT CAN COST EVERYTHING',
                                          'I DON\'T LIKE LAWYER-GUY. TYLER, ACCORDING TO PAPERS. THAT SNAKE IS DEFFENDING CRIMINALS!',
                                          'TERRY AND MATTHEW? THEY COME EARLY AS ALWAYS, AND PROBABLY ALREADY DIGGING',
                                          'SOME DAY ILL TAKE A DAY OFF. AT LEAST, I SHOULD TRY TO ATTEND AT MY FUNERALS. HA-HA-HA'],

                                  'labels':{'send_target': ['×SEND OUT'],
                                            'chat': ['×OKAY', '×HMMM..', '×YES']}}}

        self.thoughts = {'start1': 'NEW DAY, NEW JOY...',
                         'start2': 'BOSS CALLED FOR ME, I SHOULD TALK TO HIM',
                         'start3': 'NO NEED TO GO THERE YET, I SHOULD TALK TO MY BOSS FIRST',

                         '1st_case': 'TODAY\'S CASE FIRST CLUE IS {}. I NEED TO CHECK MY COMPUTER OR SEARCH IN ARCHIVES, I THINK. AS USUAL', # I NEED TO GET TO MY OFFICE TO START INVESTIGATION
                         '1st_ikit': 'OK, NOW I NEED TO ANALYSE THAT ON MY COMPUTER...',
                         '1st_made_ikit': 'RIGHT NOW I NEED TO SEND OUT SUSPECT\'S FINALIZED IDENTIKIT. WHERE IS ROB?',
                         '1st_ikit_send_out': 'NOW LET\'S TAKE A BREAK. TIME TO GET SOME COFFEE AND THEN CHECK JAIL',
                         '1st_jail_w/susp': 'OHH, A LOT OF SPEAKING IS GOING TO BE HAPPEND RIGHT NOW...',

                         'jail_w/susp': 'INTERROGATION OF THE DETAINED SUSPECTS. AGAIN AND AGAIN',
                         'new_ikit': 'I\'VE GOT A NEW TRY ON SUSPECT\'S IDENTIKIT',
                         'made_ikit': 'I\'VE GOT SUSPECT\'S FINALIZED IDENTIKIT',

                         'win1': 'I\'VE GOT YA, YOU, CRIMINAL SCUM! BOSS NEED TO KNOW ABOUT THAT',
                         'win2': 'IT\'S BETTER TO REPORT MY BOSS, NO NEED TO HANG AROUND'}

                         # 'no_case': 'WHAT AM I DOING?FOR WHAT PURPOSE DO I NEED THIS NOW?BETTER LEAVE IT ALONE',
                         # 'new_case': 'HMMM...NEW CASE IS {}.SO WHAT SHOULD I DO...',
                         # 'empty_ikit': 'IT SEEMS,I FORGOT TO TAKE AN IDENTIKIT.EH...I NEED A LOOONG VACATION',
                         # 'new_clue_added': 'I\'VE GOT A NEW CLUE!NEED TO CHECK IT ON MY COMPUTER'
                         # 'touch_entrance': 'IT\'S TOO EARLY TO GO HOME.I NEED TO EARN SOME BUCKS'


        # Текст, отображаемый в окне TODOLIST
        todolist_text = ['TRY TO SEARCH IN ARCHIVE FOR NEW CLUES',
                         'ASK WITNESESS, IF THEY HAVE COME TO THE STATION',
                         'MAKE AN IDENTIKITS, EVEN WRONG ONES',
                         'INTERROGATE DETAINED SUSPECTS WITH NO MERCY',
                         'AFTER ALL, SOLVE THE CASE AND FIND THE CRIMINAL',
                         'NOTE: NEED TO COMMUNICATE WITH COWORKERS AND WALK MORE']

        icons_list = [sheet1[154].copy(), sheet1[187].copy(), sheet1[49].copy(),
                      sheet1[138].copy(), sheet1[153].copy(), sheet1[57].copy()]
        tl_list = []
        surf_height = 0
        for s in todolist_text:
            t = text_mono.render_text(s, self.tile_font, 1, 14)
            tl_list.append(t)
            surf_height += t.get_height()-TS

        self.todolist_surf = pygame.Surface((TS*15, surf_height+TS*12))
        self.todolist_surf.set_colorkey(pygame.Color('black'))

        blit_pos_y = 0
        for x, s in enumerate(tl_list):
            h = s.get_height()
            self.todolist_surf.blit(icons_list[x], (0, blit_pos_y))
            self.todolist_surf.blit(s, (TS, blit_pos_y))
            blit_pos_y += h+TS


        # Титры
        titles_text = ['DEMO FOR TOYBOXJAM 3 (2022), HOSTED BY TOM HALL',
                       '@THATTOMHALL',
                       'SPECIAL THANKS TO:',
                       'ANATOLII MIKKIRUS - TEXTS, GAME DESIGN ADVISES, TESTING',
                       'VIKTORIYA PLAKHOTNIAIA - BRAINSTORMING, TESTING, PATIENCE, LOVE',
                       'MIKHAIL PANIN - SPELLCHECK',
                       'MIKHAIL FELDMAN - TESTING',
                       '... AND YOU!',
                       'A GAME BY PAUL RZHAVYN, 03-22.02.2022',
                       '@_SOOCHIKO']

        icons_list = [self.pico8_symbols['ball'], self.pico8_symbols['suriken'],
                      self.pico8_symbols['eye'],self.pico8_symbols['man'], self.pico8_symbols['house'],
                      self.pico8_symbols['heart'], self.pico8_symbols['star'], self.pico8_symbols['face'],
                      self.pico8_symbols['starship'], self.pico8_symbols['mask']]

        tl_list = []
        surf_height = 0
        for s in titles_text:
            t = text_mono.render_text(s, self.tile_font, 1, 14)
            tl_list.append(t)
            surf_height += t.get_height()-TS

        self.titles_surf = pygame.Surface((TS*15, surf_height+TS*20))
        self.titles_surf.set_colorkey(pygame.Color('black'))

        blit_pos_y = 0
        for x, s in enumerate(tl_list):
            h = s.get_height()
            self.titles_surf.blit(icons_list[x], (0, blit_pos_y))
            self.titles_surf.blit(s, (TS, blit_pos_y))
            blit_pos_y += h+TS



        # Надписи на окнах с иконками PICO8 для подсказок управления
        # 'down' = 'Ã'
        # 'left' = 'Ë'
        # 'o' = 'Î'
        # 'right' = 'Ñ'
        # 'up' = 'Ô'
        # 'x' = '×'
        self.labels = {'quit':None, 'try':None, 'make':None, 'no':None, 'yes':None, 'got_it':None,
                       'left':None, 'right':None, 'up':None, 'down':None,
                       '1':None, '2':None,
                       'interr':None, 'case':None, 'hints':None, 'hint':None, '/4':None,
                       'mytodo':None, 'caseN':None,'susp':None, 'ikit':None}
        label_text = ['ÎQUIT','TRY×','MAKE×','ÎNO','YES×','GOT IT×',
                      'Ë', 'Ñ', 'Ô', 'Ã', '1', '2',
                      'INTERROGATION:', 'CLUES:', 'HINTS:', 'HINT:', '/4',
                      'MY TODO LIST:', 'CASE #', 'SUSPECT','IDENTIKIT:']
        for i, key in enumerate(list(self.labels.keys())):
            if key in ('quit', 'no'):
                self.labels[key] = text_mono.render_text(label_text[i], self.tile_font, 1, None, settings.pico_red)
            elif key in ('try', 'make', 'yes', 'got_it'):
                self.labels[key] = text_mono.render_text(label_text[i], self.tile_font, 1, None, settings.pico_green)
            else:
                self.labels[key] = text_mono.render_text(label_text[i], self.tile_font, 1)



        # Текст в Паузе
        p_text = ['PAUSED', '?WANT TO QUIT?']
        p_list = []
        surf_width = 0
        for s in p_text:
            t = text_mono.render_text(s, self.tile_font, 1)
            p_list.append(t)
            if surf_width < t.get_width():
                surf_width = t.get_width()

        self.paused_surf = pygame.Surface((surf_width, TS*5))
        self.paused_surf.set_colorkey(pygame.Color('black'))

        self.paused_surf.blit(p_list[0], (TS*4, 0))
        self.paused_surf.blit(p_list[1], (0, TS*2))
        self.paused_surf.blit(self.labels['no'], (0, TS*4))
        self.paused_surf.blit(self.labels['yes'], (TS*10, TS*4))



        # Статус персонажа
        self.indicator_imgs = {'try_ikit': sheet1[154].copy(),'made_ikit': sheet1[49].copy(),'question':self.tile_font['!'].copy()}


        # Выбранная/заблокированная часть фоторобота
        self.ip_selected_imgs = {'lens':sheet1[154].copy(), 'locked':sheet1[74].copy()}


        # Текст в сцене Start
        s_text = ['TOYBOX', 'DETECTIVE', ' NAVIGATE', ' X CONFIRM', ' Z DENY', 'ESC PAUSE', 'PRESS ANY KEY']
        self.start_labels = []
        for s in s_text:
            t = text_mono.render_text(s, self.tile_font, 1)
            self.start_labels.append(t)


        # Копия для того, чтобы можно было отследить сколько дел раскрыто
        self.boss_new_clues = self.talks['boss']['new_clues'].copy()
        random.shuffle(self.boss_new_clues)


        # Подсказки действий
        texts = {'BossBriefroom': ['×>TALK TO BOSS'],
                 'Corridor': ['×>GO TO ARCHIVE', '×>GO TO JAIL', '×>GO TO OFFICE', '×>CHECK TIME', '×>TALK TO JANITOR'],
                 'Archive': ['×>TALK TO ARCHIVIST', '×>SEARCH IN ARCHIVE'],
                 'Jail': ['×>GO TO CORRIDOR', '×>CLIMB UP', '×>GO DOWN', '×>TALK TO LAWYER', '×>INTERROGATE SUSPECT'],
                 'Office': ['×>TALK TO LT.PATCHES', '×>TALK TO MATTHEW', '×>ENTER YOUR COMP'],
                 'Entrance': ['×>TALK TO DUTY OFFICER', '×>TALK TO WITNESS'],
                 'Start': ['×>START GAME', '×>CLIMB UP', '×>GO DOWN']}

        self.text_helpers = {}
        for room_key in list(texts.keys()):
            room_helpers = []
            for i, t in enumerate(texts[room_key]):
                if i == 0 and room_key == 'Start': # START GAME
                    room_helpers.append(text_mono.render_text(t, self.tile_font, 1, None, settings.pico_green))
                else:
                    room_helpers.append(text_mono.render_text(t, self.tile_font, 1))
            self.text_helpers[room_key] = room_helpers.copy()



        d = pygame.Surface((TS, TS*2)).convert()
        d.blit(sheet1[88], (0, 0))
        d.blit(sheet1[88], (0, TS))
        self.closing_door_img = d.copy()



        # Стрелки на интерфейсе окон
        self.active_arrows = {'L': None, 'R': None, 'U': None, 'D': None,
                              'l_L': None, 'l_R': None, 'l_U': None, 'l_D': None}
        arrow = pygame.Surface((TS, TS*2)).convert()
        arrow.blit(sheet1[119], (0, 0))
        arrow.blit(pygame.transform.flip(sheet1[119], False, True), (0, TS))
        self.active_arrows['L'] = arrow.copy()
        self.active_arrows['R'] = pygame.transform.flip(arrow, True, False)
        self.active_arrows['U'] = pygame.transform.rotate(arrow, -90)
        self.active_arrows['D'] = pygame.transform.flip(self.active_arrows['U'], False, True)

        little_arrow = sheet1[126].copy()
        self.active_arrows['l_L'] = pygame.transform.rotate(little_arrow, 90)
        self.active_arrows['l_R'] = pygame.transform.flip(self.active_arrows['l_L'], True, False)
        self.active_arrows['l_U'] = little_arrow.copy()
        self.active_arrows['l_D'] = pygame.transform.flip(little_arrow, False, True)


        # Картинки облаков пара
        imgs = [sheet3[240].copy(), sheet3[241].copy(), sheet3[242].copy(),
                sheet3[243].copy(), sheet3[244].copy()]
        self.cond_steam_imgs = []
        for i in imgs:
            img = pygame.Surface((TS, TS)).convert()
            img.set_colorkey(pygame.Color('black'))
            img.blit(i, (0, 0))
            self.cond_steam_imgs.append(img)


        # Плавающий знак вопроса
        q_img = text_mono.render_text('?', self.tile_font, 1, None, settings.pico_yellow)
        img = pygame.Surface((8, 8)).convert()
        img.fill(settings.pico_dark_gray)
        img.set_colorkey(settings.pico_dark_gray)
        img.blit(q_img, (0, 0))
        self.floating_question = img.copy()



        # Анимация (все анимации в игре типа loop)
        # animation_set = {'anim_frames': {'idle_l': [surf, ...], ...},
        #                  'anim_seq': {'idle_l': [(frame, duration), ...], ...}}

        # Графика Игрока
        player_anim_frames = {'idle_l': [], 'idle_r': [], 'run_l': [], 'run_r': [], 'climb': []}
        for num_key in list(sheet2.keys()):
            if num_key == 192:
                player_anim_frames['idle_r'].append(sheet2[num_key].copy())
            if num_key in (208, 209, 210, 211):
                player_anim_frames['run_r'].append(sheet2[num_key].copy())
            if num_key == 224:
                player_anim_frames['climb'].append(sheet2[num_key].copy())

        player_anim_frames['idle_l'].append(pygame.transform.flip(player_anim_frames['idle_r'][0], True, False))
        for s in player_anim_frames['run_r']:
            player_anim_frames['run_l'].append(pygame.transform.flip(s, True, False))
        player_anim_frames['climb'].append(pygame.transform.flip(player_anim_frames['climb'][0], True, False))

        player_anim_seq = {'idle_l': [(0, 1)], 'idle_r': [(0, 1)],
                           'run_l': [(0, 4), (1, 4), (2, 4), (3, 4)],
                           'run_r': [(0, 4), (1, 4), (2, 4), (3, 4)],
                           'climb': [(0, 4), (1, 4)]}

        self.player_anim_set = {'anim_frames': player_anim_frames, 'anim_seq': player_anim_seq}


        # Графика НПС
        npc_images = {'warrior':[], 'magnet':[], 'blue_cop':[],
                      'red_cop':[], 'green_dragon':[], 'snake':[],
                      'robot': [], 'gold_crab':[], 'flower': [],
                      'chicken': [], 'bug': [], 'snail': [], 'hat_guy': []}
        for num_key in list(sheet1.keys()):
            if num_key in (24, 25):
                npc_images['warrior'].append(sheet1[num_key].copy())
            if num_key == 96:
                npc_images['magnet'].append(sheet1[num_key].copy())
            if num_key in (98, 99):
                npc_images['blue_cop'].append(sheet1[num_key].copy())
            if num_key in (100, 101):
                npc_images['red_cop'].append(sheet1[num_key].copy())
            if num_key in (102, 103):
                npc_images['green_dragon'].append(sheet1[num_key].copy())
            if num_key in (104, 105):
                npc_images['snake'].append(sheet1[num_key].copy())
            if num_key in (110, 111):
                npc_images['robot'].append(sheet1[num_key].copy())
            if num_key == 123:
                npc_images['gold_crab'].append(sheet1[num_key].copy())
        for num_key in list(sheet4.keys()):
            if num_key in (225, 226):
                npc_images['flower'].append(sheet4[num_key].copy())
            if num_key in (227, 228, 229):
                npc_images['chicken'].append(sheet4[num_key].copy())
            if num_key in (231, 232):
                npc_images['bug'].append(sheet4[num_key].copy())
            if num_key in (236, 237):
                npc_images['snail'].append(sheet4[num_key].copy())
            if num_key in (238, 239):
                npc_images['hat_guy'].append(sheet4[num_key].copy())

        self.npc_anim_sets = {}

        anims = ['idle', 'run', 'talk']
        for npc_name_key in list(npc_images.keys()):
            anim_frames = {}
            anim_seq = {'idle':[(0, 14), (1, 14)],
                        'run':[(0, 20), (1, 20)],
                        'talk':[(0, 5), (1, 5)]}
            out_anim_set = {'anim_frames': None, 'anim_seq': None}

            if npc_name_key == 'chicken':
                # 1 кадр IDLE, по 2 кадра RUN и TALK
                anim_frames['idle'] = [npc_images['chicken'][0]]
                anim_frames['run'] = npc_images['chicken'][1:]
                anim_frames['talk'] = npc_images['chicken'][1:]
                anim_seq['idle'] = [(0, 1)]

            elif npc_name_key == 'magnet' or npc_name_key == 'gold_crab':
                # по 1 кадру IDLE, RUN и TALK
                for a in anims:
                    anim_frames[a] = npc_images[npc_name_key]
                    anim_seq[a] = [(0, 1)]

            else:
                # Анимации состоят из 2 кадров
                for a in anims:
                    anim_frames[a] = npc_images[npc_name_key]

            out_anim_set['anim_frames'] = anim_frames.copy()
            out_anim_set['anim_seq'] = anim_seq.copy()
            self.npc_anim_sets[npc_name_key] = out_anim_set.copy()


        self.coin_anim_set = {'anim_frames': {'idle': [sheet3[72].copy(), sheet3[73].copy()]},
                              'anim_seq': {'idle': [(0, 3), (1, 3)]}}

        self.coin_locs = []
        for i in range(16):
            self.coin_locs.append((i*TS, -TS))


        self.sounds = {'door': pygame.mixer.Sound(resource_path('sfx/tbj3_sfx_59_door1.wav')),
                       'scroll':pygame.mixer.Sound(resource_path('sfx/tbj3_sfx_37_pages.wav')),
                       'confirm':pygame.mixer.Sound(resource_path('sfx/tbj3_sfx_44_o.wav')),
                       'yes_interr':pygame.mixer.Sound(resource_path('sfx/tbj3_sfx_51_interr.wav')),
                       'chick':pygame.mixer.Sound(resource_path('sfx/tbj3_sfx_1_chik.wav')),
                       'win':pygame.mixer.Sound(resource_path('sfx/dc_music_24_win.wav')),

        }

        self.sounds['door'].set_volume(0.2)
        self.sounds['scroll'].set_volume(0.15)
        self.sounds['chick'].set_volume(0.25)
        self.sounds['confirm'].set_volume(0.45)
        self.sounds['yes_interr'].set_volume(0.3)

        pygame.mixer.music.load(resource_path('sfx/music_14_dark_town.wav'))
        pygame.mixer.music.set_volume(0.3)


    def clue_to_text(self, clue):
        clues = {'sword':'a','pickaxe':'b','hammer':'c','chest':'d','g_key':'e',
                 's_key':'f','bottle':'g','r_heart':'h','gun':'i','goblet':'j',
                 'gem':'k','grave':'l','bell':'m','pike':'n','skull':'o',
                 'bubble':'p','leaf':'q','coin':'r','o_lock':'s','g_apple':'t',
                 'g_heart':'u'}
        return clues[clue]


    def get_rnd_case_name(self):
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        templates = ['{}{}{}-{}{}-{}{}', '{}-{}{}{}{}-{}{}', '{}{}{}{}-{}{}-{}','{}{}-{}{}-{}{}{}']

        rnd_list = []
        for i in range(7):
            rnd_list.append(letters[random.randint(0, len(letters)-1)])
        return random.choice(templates).format(rnd_list[0],rnd_list[1],rnd_list[2],rnd_list[3],rnd_list[4],rnd_list[5],rnd_list[6])


    def make_cheat_img(self):
        # Картинка с ЧИТОМ
        self.cheat_image = pygame.Surface((TS*16, TS*17)).convert()
        self.cheat_image.set_colorkey(pygame.Color('magenta'))
        self.cheat_image.fill(pygame.Color('magenta'))

        pygame.draw.rect(self.cheat_image, pygame.Color('black'), (0, 0, TS*16, TS*17))

        # Части ФР
        u_cheat = self.identikit_parts['upper'][self.true_criminal[0]['ikit_part_num']]
        self.cheat_image.blit(u_cheat, (TS*5, TS*3))

        l_cheat = self.identikit_parts['lower'][self.true_criminal[1]['ikit_part_num']]
        self.cheat_image.blit(l_cheat, (TS*5, TS*7))

        i_p_num = self.true_criminal[2]['ikit_part_num']
        if i_p_num == self.bald_parts['hair'][0]:
            h_cheat = self.bald_parts['hair'][1]
        else:
            h_cheat = self.identikit_parts['hair'][self.true_criminal[2]['ikit_part_num']]
        self.cheat_image.blit(h_cheat, (TS*5, TS*3))

        i_p_num = self.true_criminal[3]['ikit_part_num']
        if i_p_num == self.bald_parts['facial_hair'][0]:
            fh_cheat = self.bald_parts['facial_hair'][1]
        else:
            fh_cheat = self.identikit_parts['facial_hair'][self.true_criminal[3]['ikit_part_num']]
        self.cheat_image.blit(fh_cheat, (TS*5, TS*8))

        # Иконки
        for i in range(4):
            clue_icon = self.clues_icons[self.case_main_clues[i]]
            self.cheat_image.blit(clue_icon, (0, TS*i))

        for i in range(4):
            for j in range(3):
                clue_icon = self.clues_icons[self.case_main_hints[i][j]]
                self.cheat_image.blit(clue_icon, (TS*2+j*TS, TS*i))

        for i in range(4):
            part_str = ''
            for tp in self.true_criminal:
                if tp['assigned_hint'][0] == self.case_main_clues[i]:
                    if tp['ikit_part'] == 'upper':
                        part_str = 'U'
                    elif tp['ikit_part'] == 'lower':
                        part_str = 'L'
                    elif tp['ikit_part'] == 'hair':
                        part_str = 'H'
                    elif tp['ikit_part'] == 'facial_hair':
                        part_str = 'FH'
                    break
            self.cheat_image.blit(text_mono.render_text(part_str, self.tile_font, 1), (TS*6, TS*i))


    def generate_case(self):
        # Генерация дела:
        print('>> GENERATING NEW CASE...')

        self.case_main_clues = [] # [str, str, ...]
        clues = list(self.clues_icons.keys())
        for i in range(4):
            rnd_clue = random.choice(clues)
            self.case_main_clues.append(rnd_clue)
            clues.remove(rnd_clue)
        print('\tMain clues:', self.case_main_clues)
        print('\t\t(left):', clues)

        clues_no_main = clues[:] # сохранить зацепки без основных отдельно

        self.case_main_hints = [] # [[str, ..., ...], [str, ...], ...]
        for p in self.case_main_clues:
            hint = [p]
            add_clues = random.sample(clues, 2)
            for cl in add_clues:
                hint.append(cl)
                clues.remove(cl)
            self.case_main_hints.append(hint)
        print('\tMain hints:', self.case_main_hints)

        self.case_false_hints = [] # [[str, ..., ...], [str, ...], ...]
        false_count = len(self.identikit_parts['upper']) + len(self.identikit_parts['lower']) + \
                      len(self.identikit_parts['hair']) + len(self.identikit_parts['facial_hair']) - 4 - 4 # - true_parts - 0_transp_img
        print('\t\t',false_count)

        for i in range(false_count):
            self.case_false_hints.append(random.sample(clues_no_main, 3))
        print('\tFalse hints:\n\t', self.case_false_hints, len(self.case_false_hints))

        mp_idxs = [0, 1, 2, 3]
        random.shuffle(mp_idxs)
        self.true_criminal = [{'ikit_part':'upper', 'ikit_part_num':0, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_main_hints[mp_idxs[0]][:],'mp_idx':mp_idxs[0]}, #'TRUEUPPER'
                              {'ikit_part':'lower', 'ikit_part_num':0, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_main_hints[mp_idxs[1]][:],'mp_idx':mp_idxs[1]}, #'TRUELOWER'
                              {'ikit_part':'hair', 'ikit_part_num':0, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_main_hints[mp_idxs[2]][:],'mp_idx':mp_idxs[2]}, #'TRUEHAIR '
                              {'ikit_part':'facial_hair', 'ikit_part_num':0, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_main_hints[mp_idxs[3]].copy(),'mp_idx':mp_idxs[3]}] #'TRUEFACHA'

        ip_count = [len(self.identikit_parts['upper'])-1, len(self.identikit_parts['lower'])-1,
                    len(self.identikit_parts['hair'])-1, len(self.identikit_parts['facial_hair'])-1]

        ip_taken = []
        for i, p in enumerate(self.true_criminal):
            ip = random.randint(1, ip_count[i])
            p['ikit_part_num'] = ip
            ip_taken.append(ip)

        print('\tTrue criminal parts:\n\t', ip_taken) # [upper, lower, hair, facial_hair]
        self.true_crim_ip_num = ip_taken.copy()
        print('\tparts:\n\t', self.true_criminal)



        self.false_suspects_parts = {'upper':[],'lower':[],'hair':[],'facial_hair':[]}
        n = 0
        upp = list(range(1, len(self.identikit_parts['upper'])))
        upp.remove(ip_taken[0])
        random.shuffle(upp)
        for i in upp:
            newcase = {'ikit_part':'upper', 'ikit_part_num':i, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_false_hints[n]} # 'FALSUPP'+str(n)
            self.false_suspects_parts['upper'].append(copy.deepcopy(newcase))
            n += 1

        low = list(range(1, len(self.identikit_parts['lower'])))
        low.remove(ip_taken[1])
        random.shuffle(low)
        for i in low:
            newcase = {'ikit_part':'lower', 'ikit_part_num':i, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_false_hints[n]}
            self.false_suspects_parts['lower'].append(copy.deepcopy(newcase))
            n += 1

        hai = list(range(1, len(self.identikit_parts['hair'])))
        hai.remove(ip_taken[2])
        random.shuffle(hai)
        for i in hai:
            newcase = {'ikit_part':'hair', 'ikit_part_num':i, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_false_hints[n]}
            self.false_suspects_parts['hair'].append(copy.deepcopy(newcase))
            n += 1

        fha = list(range(1, len(self.identikit_parts['facial_hair'])))
        fha.remove(ip_taken[3])
        random.shuffle(fha)
        for i in fha:
            newcase = {'ikit_part':'facial_hair', 'ikit_part_num':i, 'case':self.get_rnd_case_name(), 'assigned_hint':self.case_false_hints[n]}
            self.false_suspects_parts['facial_hair'].append(copy.deepcopy(newcase))
            n += 1

        print('\tFalse suspects parts:\n\t', len(self.false_suspects_parts['upper']), len(self.false_suspects_parts['lower']), len(self.false_suspects_parts['hair']), len(self.false_suspects_parts['facial_hair']))

        false_parts = []
        for key in list(self.false_suspects_parts.keys()):
            for part in self.false_suspects_parts[key]:
                false_parts.append(part)

        self.archive_cases = []
        self.archive_cases.extend(self.true_criminal)
        self.archive_cases.extend(false_parts)
        random.shuffle(self.archive_cases)
        print('\tArchive cases:\n\t',self.archive_cases)

        # Картинка с ЧИТОМ
        self.make_cheat_img()
