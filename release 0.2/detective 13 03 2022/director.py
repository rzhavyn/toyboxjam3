import pygame

import scenes
import settings
import resources
import npcgenerator

from objects import NPC

Vector2 = pygame.math.Vector2

class Director(object):

    def __init__(self):
        self.game_running = True

        self.current_scene = None
        self.scenelist = {}

        self.assets = resources.load()

        self.cut_scene = False
        self.paused = False

        self.npcgen = npcgenerator.NPCGenerator(self)

        # Данные для передачи между комнатами
        self.start_scene = False
        self.game_ended = False
        self.show_end_dialog = False

        self.current_thought = None
        self.player_indicator = None

        self.ikit_try = settings.IKIT_ZERO
        self.ikit_made = settings.IKIT_ZERO
        self.investigated_clues = []
        self.investigated_main_hints = {'upper':None,'lower':None,'hair':None,'facial_hair':None} # правильные подсказки/части ФР
        self.all_clues_investigated = False
        self.all_hints_investigated = False
        self.true_criminal_finded = False

        self.case_given = False
        self.first_ikit_try = False
        self.first_ikit_made = False

        self.curr_ikit_npcs = None
        self.witness_to_add = None

        self.player_go_door = False

        self.questions = {'BossBriefroom': True, 'Corridor': [False, False, False],
                          'Archive': False, 'Jail':[False, False, False, False], # L_U R_U L_D R_D
                          'Office': False, 'Entrance': False}
        self.suspects_interr = 0
        self.suspects_total = 0

        # self.generate_new_case()
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':2,'lower':1,'hair':1,'facial_hair':1})

        # Создание сцен
        self.add_scene('BossBriefroom', scenes.BossBriefroom(self))
        self.add_scene('Corridor', scenes.Corridor(self))
        self.add_scene('Archive', scenes.Archive(self))
        self.add_scene('Jail', scenes.Jail(self))
        self.add_scene('Office', scenes.Office(self))
        self.add_scene('Entrance', scenes.Entrance(self))
        self.add_scene('SearchInArchive', scenes.SearchInArchive(self))
        self.add_scene('PlayerCompIdentikit', scenes.PlayerCompIdentikit(self))
        self.add_scene('PlayerCompTodolist', scenes.PlayerCompTodolist(self))
        self.add_scene('Interrogation', scenes.Interrogation(self))

        self.add_scene('Start', scenes.Start(self))
        self.add_scene('Titles', scenes.Titles(self))

        # self.refresh_npcs_on_new_ikit()

        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':2,'lower':1,'hair':1,'facial_hair':1})
        # self.refresh_npcs_on_new_ikit()
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':2,'lower':1,'hair':2,'facial_hair':self.assets.true_crim_ip_num[3]})
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':self.assets.true_crim_ip_num[0],'lower':self.assets.true_crim_ip_num[1],'hair':self.assets.true_crim_ip_num[2],'facial_hair':self.assets.true_crim_ip_num[3]}) #
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':self.assets.true_crim_ip_num[0],'lower':self.assets.true_crim_ip_num[1],'hair':0,'facial_hair':self.assets.true_crim_ip_num[3]}) #
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':3,'lower':4,'hair':5,'facial_hair':2})
        # self.curr_ikit_npcs = self.npcgen.gen_current_ikit_npcs({'upper':0,'lower':0,'hair':0,'facial_hair':0})

        # Первая сцена
        # self.go_to('BossBriefroom', {'player_pos': settings.player_locs['BossBriefroom']['from_Corridor'],
        #                              'player_facing': '_l'})

        # self.go_to('Corridor', {'player_pos': settings.player_locs['Corridor']['from_BossBriefroom'],
        #                         'player_facing': '_r'})

        # self.go_to('Archive', {'player_pos': settings.player_locs['Archive']['from_Corridor'],
        #                        'player_facing': '_r'})

        # self.go_to('Jail', {'player_pos': settings.player_locs['Jail']['from_Corridor'],
        #                     'player_facing': '_r'})

        # self.go_to('Office', {'player_pos': settings.player_locs['Office']['from_Corridor'],
        #                       'player_facing': '_r'})

        # self.go_to('SearchInArchive', {'player_pos': Vector2(8*8, 6*8),
        #                                'player_facing': '_r'})

        # self.go_to('PlayerCompIdentikit', {'player_pos': Vector2(12*8, 6*8),
        #                                    'player_facing': '_r',
        #                                    'identikit': {'upper':1,'lower':1,'hair':2,'facial_hair':1}}) # индексы для self.identikit_parts, не для self.false_suspects_parts

        # self.go_to('PlayerCompTodolist', {'player_pos': Vector2(12*8, 6*8),
        #                                    'player_facing': '_r'})


        # f = self.curr_ikit_npcs['false_suspects'][0]['ikit_parts_cases']
        # t = self.curr_ikit_npcs['true_suspects'][0]['ikit_parts_cases']
        # self.go_to('Interrogation', {'player_pos': Vector2(8*5, 6*4),
        #                              'player_facing': '_r',
        #                              'criminal_parts':t})

        self.go_to('Start', {'player_pos': Vector2(8*7, 8*10),
                             'player_facing': '_r'})

        # self.go_to('Titles', {})


    def add_scene(self, scenename, sceneobj):
        self.scenelist[scenename] = sceneobj


    def go_to(self, scenename, transitionto_args):
        if scenename != None:
            self.current_scene = self.scenelist[scenename]
            self.current_scene.on_transitionto(transitionto_args)


    def quit(self):
        self.game_running = False


    def refresh_npcs_on_new_ikit(self):
        jail_scene = self.scenelist['Jail']
        entrance_scene = self.scenelist['Entrance']

        self.witness_to_add = None
        self.suspects_interr = 0 # текущее кол-во допрошенных в данной генерации подозреваемых
        self.suspects_total = 0 # всего

        # Очистить от предыдущих нпс
        for old_npc in list(jail_scene.all_objects.sprites()):
            if isinstance(old_npc, NPC):
                if old_npc.npc_scene_name == 'suspect':
                    old_npc.kill()
        for old_npc in list(entrance_scene.all_objects.sprites()):
            if isinstance(old_npc, NPC):
                if old_npc.npc_scene_name == 'witness':
                    old_npc.kill()

        for npc_key in list(self.curr_ikit_npcs.keys()):
            if npc_key == 'false_suspects':
                gen_npcs = self.curr_ikit_npcs['false_suspects']

                for npc in gen_npcs:
                    suspect = NPC(jail_scene, npc['loc'], npc['npc_type'], 'suspect', npc['talk_rect'], npc['ikit_parts_cases'], npc['wander_p'], npc['cell'], 35)
                    jail_scene.all_objects.add(suspect)
                    jail_scene.layered_sprites.add(suspect)

                    if npc['cell'] == 'L_U':
                        self.questions['Jail'][0] = True
                    if npc['cell'] == 'R_U':
                        self.questions['Jail'][1] = True
                    if npc['cell'] == 'L_D':
                        self.questions['Jail'][2] = True
                    if npc['cell'] == 'R_D':
                        self.questions['Jail'][3] = True

                    self.suspects_total += 1

            if npc_key == 'true_suspects':
                gen_npcs = self.curr_ikit_npcs['true_suspects']

                for npc in gen_npcs:
                    suspect = NPC(jail_scene, npc['loc'], npc['npc_type'], 'suspect', npc['talk_rect'], npc['ikit_parts_cases'], npc['wander_p'], npc['cell'], 35)
                    jail_scene.all_objects.add(suspect)
                    jail_scene.layered_sprites.add(suspect)

                    if npc['cell'] == 'L_U':
                        self.questions['Jail'][0] = True
                    if npc['cell'] == 'R_U':
                        self.questions['Jail'][1] = True
                    if npc['cell'] == 'L_D':
                        self.questions['Jail'][2] = True
                    if npc['cell'] == 'R_D':
                        self.questions['Jail'][3] = True

                    self.suspects_total += 1

            if npc_key == 'witness':
                npc = self.curr_ikit_npcs['witness']
                if npc != []:
                    self.witness_to_add = NPC(entrance_scene, npc['loc'], npc['npc_type'], 'witness', npc['talk_rect'], npc['true_case'])

        print('NUM Suspects total:', self.suspects_total)


    def generate_new_case(self):
        # Очистка
        self.ikit_try = settings.IKIT_ZERO
        self.ikit_made = settings.IKIT_ZERO
        self.investigated_clues = []
        self.investigated_main_hints = {'upper':None,'lower':None,'hair':None,'facial_hair':None} # правильные подсказки/части ФР
        self.all_clues_investigated = False
        self.all_hints_investigated = False
        self.curr_ikit_npcs = None
        self.witness_to_add = None

        self.assets.generate_case()

        self.investigated_clues.append(self.assets.case_main_clues[0]) # первая зацепка всегда выдается боссом
