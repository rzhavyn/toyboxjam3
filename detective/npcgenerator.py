import copy
import random

import pygame

import settings

TS = settings.app.TS
DEBUG = settings.DEBUG
Vector2 = pygame.math.Vector2

class NPCGenerator(object):

    def __init__(self, parent):
        self.parent = parent
        self.assets = parent.assets

        self.npc_types = ['warrior','magnet','green_dragon','snake',
                          'robot','gold_crab','flower','chicken',
                          'bug','snail','hat_guy']

        self.def_suspect = {'npc_type': None, 'loc': None, 'cell': None, 'wander_p': None, 'talk_rect': None, 'ikit_parts_cases':[]} # 'arch_cases'
        self.def_witness = {'npc_type': None, 'loc': None, 'talk_rect': None, 'true_case': None}

        self.jail_locs = {'L_U':[Vector2(TS*2, TS*3), Vector2(TS*3, TS*3)], 'L_D':[Vector2(TS*2, TS*6), Vector2(TS*3, TS*6)],
                          'R_U':[Vector2(TS*12, TS*3), Vector2(TS*13, TS*3)], 'R_D':[Vector2(TS*12, TS*6), Vector2(TS*13, TS*6)]}
        self.jail_locs_keys = []

        self.talk_rects = {'L_U':pygame.Rect(TS*5, TS*3, TS, TS), 'L_D':pygame.Rect(TS*5, TS*6, TS, TS),
                           'R_U':pygame.Rect(TS*10, TS*3, TS, TS), 'R_D':pygame.Rect(TS*10, TS*6, TS, TS)}

        self.entrance_locs = {'L':{'loc':Vector2(TS*8, TS*5),'talk_rect':pygame.Rect(TS*8, TS*6, TS, TS)},
                              'M':{'loc':Vector2(TS*10, TS*5),'talk_rect':pygame.Rect(TS*10, TS*6, TS, TS)},
                              'R':{'loc':Vector2(TS*12, TS*5),'talk_rect':pygame.Rect(TS*12, TS*6, TS, TS)}}

        self.current_mp_used_n = 0

        self.used = []

        self.upper_used = []
        self.lower_used = []
        self.hair_used = []
        self.facial_hair_used = []


    def get_rnd_ip(self, ip, used_list, pick_from):
        out = None
        gen = True
        while gen:
            rnd_ip = random.choice(pick_from[ip])
            if rnd_ip not in used_list:
                used_list.append(rnd_ip)
                out = rnd_ip
                gen = False
        return out


    def gen_false_suspects(self, num_false_suspects, false_ikit_cases):
        false_suspects = []

        for i in range(num_false_suspects):
            out = [None, None, None, None]

            f_suspect = self.def_suspect.copy()
            f_suspect['npc_type'] = random.choice(self.npc_types)

            loc = random.choice(self.jail_locs_keys)
            self.jail_locs_keys.remove(loc)
            rnd_loc = random.choice(self.jail_locs[loc])
            f_suspect['loc'] = rnd_loc
            self.jail_locs[loc].remove(rnd_loc)
            f_suspect['wander_p'] = self.jail_locs[loc][0]
            f_suspect['talk_rect'] = self.talk_rects[loc]
            f_suspect['cell'] = loc

            if false_ikit_cases == []:
                # Все случайные
                out[0] = self.get_rnd_ip('upper', self.upper_used, self.assets.false_suspects_parts)
                out[1] = self.get_rnd_ip('lower', self.lower_used, self.assets.false_suspects_parts)
                out[2] = self.get_rnd_ip('hair', self.hair_used, self.assets.false_suspects_parts)
                out[3] = self.get_rnd_ip('facial_hair', self.facial_hair_used, self.assets.false_suspects_parts)

            else:
                if len(false_ikit_cases) <= 2:
                    # 1 или 2 части берутся из false_ikit_cases
                    if len(false_ikit_cases) == 1:
                        n_false = 1
                    elif len(false_ikit_cases) == 2:
                        n_false = random.randint(1, 2)

                    false_ikit_cases_copy = copy.deepcopy(false_ikit_cases)
                    for j in range(n_false):
                        rnd_ic = random.choice(false_ikit_cases_copy)
                        false_ikit_cases_copy.remove(rnd_ic)
                        if rnd_ic['ikit_part'] == 'upper':
                            out[0] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'lower':
                            out[1] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'hair':
                            out[2] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'facial_hair':
                            out[3] = rnd_ic

                    # Остальные случайные
                    if not out[0]:
                        out[0] = self.get_rnd_ip('upper', self.upper_used, self.assets.false_suspects_parts)
                    if not out[1]:
                        out[1] = self.get_rnd_ip('lower', self.lower_used, self.assets.false_suspects_parts)
                    if not out[2]:
                        out[2] = self.get_rnd_ip('hair', self.hair_used, self.assets.false_suspects_parts)
                    if not out[3]:
                        out[3] = self.get_rnd_ip('facial_hair', self.facial_hair_used, self.assets.false_suspects_parts)
                else:
                    # Все случайные
                    out[0] = self.get_rnd_ip('upper', self.upper_used, self.assets.false_suspects_parts)
                    out[1] = self.get_rnd_ip('lower', self.lower_used, self.assets.false_suspects_parts)
                    out[2] = self.get_rnd_ip('hair', self.hair_used, self.assets.false_suspects_parts)
                    out[3] = self.get_rnd_ip('facial_hair', self.facial_hair_used, self.assets.false_suspects_parts)

            f_suspect['ikit_parts_cases'] = copy.deepcopy(out)

            if DEBUG: print('\tFALSE SUSPECT:', f_suspect)
            false_suspects.append(f_suspect.copy())
        return false_suspects


    def gen_witness(self):
        c_witness = self.def_witness.copy()
        c_witness['npc_type'] = random.choice(self.npc_types)

        rnd_loc = random.choice(list(self.entrance_locs.keys()))
        c_witness['loc'] = self.entrance_locs[rnd_loc]['loc']
        c_witness['talk_rect'] = self.entrance_locs[rnd_loc]['talk_rect']

        used_iparts = []
        for p in self.used:
            used_iparts.append(p['ikit_part'])

        left_unused = []
        for tc in self.assets.true_criminal:
            if tc['ikit_part'] not in used_iparts:
                left_unused .append(tc)

        if DEBUG:print('\t\tleft unused:', left_unused)

        if left_unused != []:
            if DEBUG:print('\t\tikit part for witness: {}'.format(left_unused[0]))
            c_witness['true_case'] = left_unused[0]
            self.used.append(left_unused[0])

            if DEBUG: print('\tWITNESS:', c_witness)
            return c_witness

        else:
            if DEBUG:print('\t\tNo free main hints for witness')
            return []


    def gen_true_suspects(self, true_ikit_cases, false_ikit_cases):
        true_suspects = []

        if not self.parent.all_hints_investigated:
            add_hint_idx = random.randint(0, len(true_ikit_cases)-1)
            if DEBUG: print('\tSuspect idx to add hint:', add_hint_idx)

            # Подходящие подозреваемые по числу подходящих частей
            for i in range(len(true_ikit_cases)):
                out = [None, None, None, None]

                t_suspect = self.def_suspect.copy()
                t_suspect['npc_type'] = random.choice(self.npc_types)

                loc = random.choice(self.jail_locs_keys)
                self.jail_locs_keys.remove(loc)
                rnd_loc = random.choice(self.jail_locs[loc])
                t_suspect['loc'] = rnd_loc
                self.jail_locs[loc].remove(rnd_loc)
                t_suspect['wander_p'] = self.jail_locs[loc][0]
                t_suspect['talk_rect'] = self.talk_rects[loc]
                t_suspect['cell'] = loc

                true_ikit_part = true_ikit_cases[i]
                print('\t\ttrue_ikit_part:', true_ikit_part)

                # Добавить одну подсказку в дополнение к подходящей части
                if i == add_hint_idx:
                    # если ли зацепка из true_ikit_part в investigated_clues
                    if not true_ikit_part['assigned_hint'][0] in self.parent.investigated_clues:
                        print('\t\ttrue_ikit_part main clue {} NOT in investigated_clues {}'.format(true_ikit_part['assigned_hint'][0], self.parent.investigated_clues))
                        # вгенеировать true_ikit_part
                        if true_ikit_part['ikit_part'] == 'upper':
                            out[0] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'lower':
                            out[1] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'hair':
                            out[2] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'facial_hair':
                            out[3] = true_ikit_part
                        # добавть в использованные в генерации
                        self.used.append(true_ikit_part)

                        # + вгенерировать доп true_cur_part по одной зацепке, если ее нет в investigated_main_hints:
                        # найти зацепку, у которой нет hint
                        clues_without_hint = []
                        for c in self.parent.investigated_clues:
                            for p in list(self.parent.investigated_main_hints.values()):
                                if p != None:
                                    if p['assigned_hint'][0] != c:
                                        if c not in clues_without_hint:
                                            clues_without_hint.append(c)
                                else:
                                    if c not in clues_without_hint:
                                        clues_without_hint.append(c)

                        print('\t\tclues_without_hint {}'.format(clues_without_hint))

                        clue_part = None
                        # найти часть true_criminal, соотв этой зацепке
                        if clues_without_hint != []:
                            for tp in self.assets.true_criminal:
                                if tp['assigned_hint'][0] == clues_without_hint[0]:
                                    clue_part = tp
                                    break

                            print('\t\t+ clue_part to suspect: {}'.format(clue_part))

                            if clue_part['ikit_part'] == 'upper':
                                out[0] = clue_part
                            elif clue_part['ikit_part'] == 'lower':
                                out[1] = clue_part
                            elif clue_part['ikit_part'] == 'hair':
                                out[2] = clue_part
                            elif clue_part['ikit_part'] == 'facial_hair':
                                out[3] = clue_part
                            # добавть в использованные в генерации
                            self.used.append(clue_part)

                    else:
                        print('\t\ttrue_ikit_part main clue {} IN investigated_clues {}'.format(true_ikit_part['assigned_hint'][0], self.parent.investigated_clues))
                        # проверить есть ли зацепка в investigated_main_hints
                        # найти зацепку, у которой нет hint
                        clue_in_main_hints = False
                        for p in list(self.parent.investigated_main_hints.values()):
                            if p != None:
                                if p['assigned_hint'][0] == true_ikit_part['assigned_hint'][0]:
                                    clue_in_main_hints = True
                                    break
                        # если нет:
                        if not clue_in_main_hints:
                            # вгенеировать true_ikit_part
                            if true_ikit_part['ikit_part'] == 'upper':
                                out[0] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'lower':
                                out[1] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'hair':
                                out[2] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'facial_hair':
                                out[3] = true_ikit_part
                            # добавть в использованные в генерации
                            self.used.append(true_ikit_part)
                        # если есть:
                        else:
                            # Добавить ее еще раз
                            # вгенеировать true_ikit_part
                            if true_ikit_part['ikit_part'] == 'upper':
                                out[0] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'lower':
                                out[1] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'hair':
                                out[2] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'facial_hair':
                                out[3] = true_ikit_part
                            # добавть в использованные в генерации
                            self.used.append(true_ikit_part)

                else:
                    # Вгенерировать одну подходящую часть ФР
                    # если ли зацепка из true_ikit_part в investigated_clues
                    if not true_ikit_part['assigned_hint'][0] in self.parent.investigated_clues:
                        print('\t\ttrue_ikit_part main clue {} NOT in investigated_clues {}'.format(true_ikit_part['assigned_hint'][0], self.parent.investigated_clues))
                        # вгенеировать true_ikit_part
                        if true_ikit_part['ikit_part'] == 'upper':
                            out[0] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'lower':
                            out[1] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'hair':
                            out[2] = true_ikit_part
                        elif true_ikit_part['ikit_part'] == 'facial_hair':
                            out[3] = true_ikit_part
                        # добавть в использованные в генерации
                        self.used.append(true_ikit_part)
                    else:
                        print('\t\ttrue_ikit_part main clue {} IN investigated_clues {}'.format(true_ikit_part['assigned_hint'][0], self.parent.investigated_clues))
                        # проверить есть ли зацепка в investigated_main_hints
                        # найти зацепку, у которой нет hint
                        clue_in_main_hints = False
                        for p in list(self.parent.investigated_main_hints.values()):
                            if p != None:
                                if p['assigned_hint'][0] == true_ikit_part['assigned_hint'][0]:
                                    clue_in_main_hints = True
                                    break
                        # если нет:
                        if not clue_in_main_hints:
                            # вгенеировать true_ikit_part
                            if true_ikit_part['ikit_part'] == 'upper':
                                out[0] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'lower':
                                out[1] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'hair':
                                out[2] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'facial_hair':
                                out[3] = true_ikit_part
                            # добавть в использованные в генерации
                            self.used.append(true_ikit_part)
                        else:
                            # Добавить ее еще раз #2
                            # вгенеировать true_ikit_part
                            if true_ikit_part['ikit_part'] == 'upper':
                                out[0] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'lower':
                                out[1] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'hair':
                                out[2] = true_ikit_part
                            elif true_ikit_part['ikit_part'] == 'facial_hair':
                                out[3] = true_ikit_part
                            # добавть в использованные в генерации
                            self.used.append(true_ikit_part)


                print('\t\tUSED main hints:', self.used)
                print('\t\tout:', out)

                if false_ikit_cases == []:
                    # Остальные случайные
                    if true_ikit_cases[i]['ikit_part'] != 'upper':
                        out[0] = self.get_rnd_ip('upper', self.upper_used, self.assets.false_suspects_parts)
                    if true_ikit_cases[i]['ikit_part'] != 'lower':
                        out[1] = self.get_rnd_ip('lower', self.lower_used, self.assets.false_suspects_parts)
                    if true_ikit_cases[i]['ikit_part'] != 'hair':
                        out[2] = self.get_rnd_ip('hair', self.hair_used, self.assets.false_suspects_parts)
                    if true_ikit_cases[i]['ikit_part'] != 'facial_hair':
                        out[3] = self.get_rnd_ip('facial_hair', self.facial_hair_used, self.assets.false_suspects_parts)
                else:
                    # 1 или 2 части берутся из false_ikit_cases
                    if len(false_ikit_cases) == 1:
                        n_false = 1
                    elif len(false_ikit_cases) > 1:
                        n_false = random.randint(1, 2)

                    print('\t\tn_false:', n_false)
                    print('\t\tfalse_ikit_cases:', false_ikit_cases)

                    false_ikit_cases_copy = copy.deepcopy(false_ikit_cases)

                    used_ips = []
                    for up in self.used:
                        used_ips.append(up['ikit_part'])

                    for j in range(n_false):
                        for k in range(len(false_ikit_cases_copy)):
                            rnd_ic = random.choice(false_ikit_cases_copy)
                            if rnd_ic['ikit_part'] in used_ips:
                                false_ikit_cases_copy.remove(rnd_ic)

                        print('\t\t\trnd pick:', rnd_ic)

                        if rnd_ic['ikit_part'] == 'upper':
                            out[0] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'lower':
                            out[1] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'hair':
                            out[2] = rnd_ic
                        elif rnd_ic['ikit_part'] == 'facial_hair':
                            out[3] = rnd_ic

                    if not all(out):
                        # Дополнить случайными до 4 частей
                        if out[0] == None:
                            out[0] = self.get_rnd_ip('upper', self.upper_used, self.assets.false_suspects_parts)
                        if out[1] == None:
                            out[1] = self.get_rnd_ip('lower', self.lower_used, self.assets.false_suspects_parts)
                        if out[2] == None:
                            out[2] = self.get_rnd_ip('hair', self.hair_used, self.assets.false_suspects_parts)
                        if out[3] == None:
                            out[3] = self.get_rnd_ip('facial_hair', self.facial_hair_used, self.assets.false_suspects_parts)

                t_suspect['ikit_parts_cases'] = copy.deepcopy(out)

                if DEBUG: print('\tTRUE SUSPECT:', t_suspect)
                true_suspects.append(t_suspect.copy())


        else:
            out = [None, None, None, None]

            t_suspect = self.def_suspect.copy()
            t_suspect['npc_type'] = random.choice(self.npc_types)

            loc = random.choice(self.jail_locs_keys)
            self.jail_locs_keys.remove(loc)
            rnd_loc = random.choice(self.jail_locs[loc])
            t_suspect['loc'] = rnd_loc
            self.jail_locs[loc].remove(rnd_loc)
            t_suspect['wander_p'] = self.jail_locs[loc][0]
            t_suspect['talk_rect'] = self.talk_rects[loc]
            t_suspect['cell'] = loc

            out[0] = self.assets.true_criminal[0]
            out[1] = self.assets.true_criminal[1]
            out[2] = self.assets.true_criminal[2]
            out[3] = self.assets.true_criminal[3]

            t_suspect['ikit_parts_cases'] = copy.deepcopy(out)

            print('\tTRUE CRIMINAL!:', t_suspect)
            true_suspects.append(t_suspect.copy())

        return true_suspects


    def gen_current_ikit_npcs(self, ikit):
        if DEBUG: print('>GEN NEW CURRENT NPCS<')
        curr_ikit_npcs = {'false_suspects':[],'true_suspects':[],'witness':[]}

        self.upper_used = []
        self.lower_used = []
        self.hair_used = []
        self.facial_hair_used = []

        self.used = []

        self.jail_locs = {'L_U':[Vector2(TS*2, TS*3), Vector2(TS*3, TS*3)], 'L_D':[Vector2(TS*2, TS*6), Vector2(TS*3, TS*6)],
                          'R_U':[Vector2(TS*12, TS*3), Vector2(TS*13, TS*3)], 'R_D':[Vector2(TS*12, TS*6), Vector2(TS*13, TS*6)]}

        # Определить, какие части и в каком кол-ве содержит собранный игроком ФР
        true_ikit_cases = []
        false_ikit_cases = []

        if ikit['upper'] == self.assets.true_crim_ip_num[0]:
            true_ikit_cases.append(self.assets.true_criminal[0])
        elif ikit['upper'] != 0:
            for fp in self.assets.false_suspects_parts['upper']:
                if fp['ikit_part_num'] == ikit['upper']:
                    false_ikit_cases.append(fp)
                    break

        if ikit['lower'] == self.assets.true_crim_ip_num[1]:
            true_ikit_cases.append(self.assets.true_criminal[1])
        elif ikit['lower'] != 0:
            for fp in self.assets.false_suspects_parts['lower']:
                if fp['ikit_part_num'] == ikit['lower']:
                    false_ikit_cases.append(fp)
                    break

        if ikit['hair'] == self.assets.true_crim_ip_num[2]:
            true_ikit_cases.append(self.assets.true_criminal[2])
        elif ikit['hair'] != 0:
            for fp in self.assets.false_suspects_parts['hair']:
                if fp['ikit_part_num'] == ikit['hair']:
                    false_ikit_cases.append(fp)
                    break

        if ikit['facial_hair'] == self.assets.true_crim_ip_num[3]:
            true_ikit_cases.append(self.assets.true_criminal[3])
        elif ikit['facial_hair'] != 0:
            for fp in self.assets.false_suspects_parts['facial_hair']:
                if fp['ikit_part_num'] == ikit['facial_hair']:
                    false_ikit_cases.append(fp)
                    break

        if DEBUG: print('\tTrue cases:',true_ikit_cases)
        if DEBUG: print('\ttrue_ip:', len(true_ikit_cases),'false_ip:', len(false_ikit_cases))

        # ФР не содержит никаких частей ФР вообще
        if len(true_ikit_cases) == 0 and len(false_ikit_cases) == 0:
            if DEBUG: print('1 CASE: true_ikit_cases= 0 false_ikit_cases= 0')
            self.jail_locs_keys = list(self.jail_locs.keys())
            self.current_mp_used_n = len(self.parent.investigated_clues)-1
            num_false_suspects = random.randint(1, 3)
            curr_ikit_npcs['false_suspects'] = self.gen_false_suspects(num_false_suspects, false_ikit_cases)
            curr_ikit_npcs['witness'] = self.gen_witness()

        # ФР содержит 1--несколько правильных частей,остальные части пусты
        if len(true_ikit_cases) != 0 and len(false_ikit_cases) == 0:
            if DEBUG: print('2 CASE: true_ikit_cases=', len(true_ikit_cases), 'false_ikit_cases=0')
            self.jail_locs_keys = list(self.jail_locs.keys())
            self.current_mp_used_n = len(self.parent.investigated_clues)-1
            curr_ikit_npcs['true_suspects'] = self.gen_true_suspects(true_ikit_cases, [])
            num_false_suspects = 4 - len(true_ikit_cases)
            if num_false_suspects != 0:
                curr_ikit_npcs['false_suspects'] = self.gen_false_suspects(num_false_suspects, [])
            curr_ikit_npcs['witness'] = self.gen_witness()

        # ФР содержит 1--несколько правильных частей, остальные части заполнены ложными частями ФР
        if len(true_ikit_cases) != 0 and len(false_ikit_cases) != 0:
            if DEBUG: print('3 CASE: true_ikit_cases=', len(true_ikit_cases), 'false_ikit_cases=', len(false_ikit_cases))
            self.jail_locs_keys = list(self.jail_locs.keys())
            self.current_mp_used_n = len(self.parent.investigated_clues)-1
            curr_ikit_npcs['true_suspects'] = self.gen_true_suspects(true_ikit_cases, false_ikit_cases)
            num_false_suspects = 4 - len(true_ikit_cases)
            if num_false_suspects != 0:
                curr_ikit_npcs['false_suspects'] = self.gen_false_suspects(num_false_suspects, false_ikit_cases)
            curr_ikit_npcs['witness'] = self.gen_witness()

        # ФР состоит только из 1--нескольких ложный частей
        if len(true_ikit_cases) == 0 and len(false_ikit_cases) != 0:
            if DEBUG: print('4 CASE: true_ikit_cases=0 false_ikit_cases=', len(false_ikit_cases))
            self.jail_locs_keys = list(self.jail_locs.keys())
            self.current_mp_used_n = len(self.parent.investigated_clues)-1
            num_false_suspects = random.randint(1, 3)
            curr_ikit_npcs['false_suspects'] = self.gen_false_suspects(num_false_suspects, false_ikit_cases)
            curr_ikit_npcs['witness'] = self.gen_witness()

        return curr_ikit_npcs
