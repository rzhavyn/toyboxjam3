import random
import copy

import pygame

import text_mono
import objects
import settings

TS = settings.app.TS
WIN_W = settings.app.DISP_W
WIN_H = settings.app.DISP_H
DEBUG = settings.DEBUG
Vector2 = pygame.math.Vector2

FADEINOUT_DURATION = 16
FADEINOUT_DURATION_SPLASH = 60
BB_GROUND = 7*TS+1
SHOW_ARROW_DURATION = 3
PAUSED_ALPHA = 200


class Scene(object):

    def on_transitionto(self):
        raise NotImplementedError('on_transitionto method must be defined in subclass.')

    def handle_events(self, events):
        raise NotImplementedError('handle_events method must be defined in subclass.')

    def update(self, delta):
        raise NotImplementedError('update method must be defined in subclass.')

    def render(self, screen):
        raise NotImplementedError('render method must be defined in subclass.')


class BossBriefroom(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'BossBriefroom'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.boss_tmx)
        self.map_bounding_box = pygame.Rect(2*TS-1, 0, 16*TS+1, BB_GROUND)

        self.passage_to_corridor = objects.Passage(self, Vector2(15*TS+1, 5*TS), 'BossBriefroom', 'Corridor', Vector2(1, 0))
        self.all_objects.add(self.passage_to_corridor)
        self.layered_sprites.add(self.passage_to_corridor)

        self.boss = objects.NPC(self, Vector2(3*TS, 5*TS), 'red_cop', 'boss', pygame.Rect(2*TS, 5*TS, 3*TS, 2*TS))
        self.all_objects.add(self.boss)
        self.layered_sprites.add(self.boss)

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 11*TS), Vector2(0, -1))

        self.start_spawning_coins = False
        self.spawn_timer = 3
        self.coin_locs = self.assets.coin_locs.copy()

        cond = objects.ParticleEmitter(self, Vector2(TS*7+TS/2, TS/2))
        self.cond_group = [cond]

        self.q_boss = objects.FloatingImage(self, Vector2(TS*3, TS*4-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_boss)
        self.layered_sprites.add(self.q_boss)


    def spawn_coin(self):
        pos = random.choice(self.coin_locs)

        c = objects.Coin(self, Vector2(pos))
        self.all_objects.add(c)
        self.layered_sprites.add(c)


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        self.dialogue_box.show_thoughts(self.director.current_thought)

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        if self.start_spawning_coins:
            if self.spawn_timer >= 0:
                self.spawn_timer -= 1

                if self.spawn_timer == 0:
                    self.spawn_timer = random.randint(1, 2)
                    self.spawn_coin()

        for c in self.cond_group:
            c.update(delta)

        self.q_boss.show = self.director.questions[self.scene_name]
        # if not self.director.case_given or self.director.game_ended:
        #     self.q_boss.show = True
        # else:
        #     self.q_boss.show = False

        self.all_objects.update(delta)

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()


        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects from here:
        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.boss.talk_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))




class Corridor(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Corridor'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.corridor_tmx)
        self.map_bounding_box = pygame.Rect(-2*TS-1, 0, 19*TS+1, BB_GROUND)

        self.passage_to_boss = objects.Passage(self, Vector2(-TS, 5*TS), 'Corridor', 'BossBriefroom', Vector2(-1, 0))
        self.all_objects.add(self.passage_to_boss)
        self.layered_sprites.add(self.passage_to_boss)

        self.door_to_archive = objects.Door(self, Vector2(3*TS, 5*TS), 'Corridor', 'Archive')
        self.all_objects.add(self.door_to_archive)
        self.layered_sprites.add(self.door_to_archive)

        self.door_to_jail = objects.Door(self, Vector2(7*TS, 5*TS), 'Corridor', 'Jail')
        self.all_objects.add(self.door_to_jail)
        self.layered_sprites.add(self.door_to_jail)

        self.door_to_office = objects.Door(self, Vector2(11*TS, 5*TS), 'Corridor', 'Office')
        self.all_objects.add(self.door_to_office)
        self.layered_sprites.add(self.door_to_office)

        self.passage_to_entrance = objects.Passage(self, Vector2(15*TS, 5*TS), 'Corridor', 'Entrance', Vector2(1, 0))
        self.all_objects.add(self.passage_to_entrance)
        self.layered_sprites.add(self.passage_to_entrance)

        self.janitor = objects.NPC(self, Vector2(3*TS, 5*TS), 'blue_cop', 'janitor', pygame.Rect(2*TS, 5*TS, 3*TS, TS))
        self.all_objects.add(self.janitor)
        self.layered_sprites.add(self.janitor)

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 12*TS), Vector2(0, -1))

        cond = objects.ParticleEmitter(self, Vector2(TS*7+TS/2, TS/2))
        self.cond_group = [cond]

        self.q_archive = objects.FloatingImage(self, Vector2(3*TS+TS/2, 4*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_archive)
        self.layered_sprites.add(self.q_archive)

        self.q_jail = objects.FloatingImage(self, Vector2(7*TS+TS/2, 4*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_jail)
        self.layered_sprites.add(self.q_jail)

        self.q_office = objects.FloatingImage(self, Vector2(11*TS+TS/2, 4*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_office)
        self.layered_sprites.add(self.q_office)


    def get_randomised_janitor_pos(self):
        loc = {(TS, 6*TS): pygame.Rect(TS, 6*TS, 2*TS, TS), (2*TS, 6*TS): pygame.Rect(TS, 6*TS, 2*TS, TS),
               (5*TS, 6*TS): pygame.Rect(5*TS, 6*TS, 2*TS, TS), (6*TS, 6*TS): pygame.Rect(5*TS, 6*TS, 2*TS, TS),
               (9*TS, 6*TS): pygame.Rect(9*TS, 6*TS, 2*TS, TS), (10*TS, 6*TS): pygame.Rect(9*TS, 6*TS, 2*TS, TS),
               (13*TS, 6*TS): pygame.Rect(13*TS, 6*TS, 2*TS, TS), (14*TS, 6*TS): pygame.Rect(13*TS, 6*TS, 2*TS, TS)}
        rnd_loc = random.choice(list(loc.keys()))
        return Vector2(rnd_loc), loc[rnd_loc]


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        if self.director.true_criminal_finded:
            self.director.start_scene = True

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        self.dialogue_box.show_thoughts(self.director.current_thought)

        self.janitor.pos, self.janitor.talk_rect = self.get_randomised_janitor_pos()

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        for c in self.cond_group:
            c.update(delta)

        self.q_archive.show = self.director.questions[self.scene_name][0]
        self.q_jail.show = self.director.questions[self.scene_name][1]
        self.q_office.show = self.director.questions[self.scene_name][2]

        self.all_objects.update(delta)

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.janitor.talk_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))




class Archive(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Archive'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.archive_tmx)
        self.map_bounding_box = pygame.Rect(-2*TS-1, 0, 15*TS+1, BB_GROUND)

        self.passage_to_corridor = objects.Passage(self, Vector2(-TS, 5*TS), 'Archive', 'Corridor', Vector2(-1, 0))
        self.all_objects.add(self.passage_to_corridor)
        self.layered_sprites.add(self.passage_to_corridor)

        self.archivist = objects.NPC(self, Vector2(6*TS, 5*TS), 'blue_cop', 'archivist', pygame.Rect(5*TS, 5*TS, 2*TS, 2*TS))
        self.all_objects.add(self.archivist)
        self.layered_sprites.add(self.archivist)

        self.archive_comp = objects.InteractionObject(self, Vector2(7*TS, 6*TS), (2*TS, TS), pygame.Rect(7*TS, 6*TS, 2*TS, TS),
                                                      'archive_comp', self.scene_name, True, 'SearchInArchive')
        self.all_objects.add(self.archive_comp)
        self.layered_sprites.add(self.archive_comp)

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 11*TS), Vector2(0, -1))

        cond = objects.ParticleEmitter(self, Vector2(TS*5+TS/2, TS/2))
        cond2 = objects.ParticleEmitter(self, Vector2(TS*9+TS/2, TS/2))
        self.cond_group = [cond, cond2]

        self.q_archive_comp = objects.FloatingImage(self, Vector2(7*TS+TS/2, 4*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_archive_comp)
        self.layered_sprites.add(self.q_archive_comp)


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        if 'cut_scene' in list(transitionto_args.keys()):
            self.director.cut_scene = transitionto_args['cut_scene']

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        self.dialogue_box.show_thoughts(self.director.current_thought)

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        for c in self.cond_group:
            c.update(delta)

        self.q_archive_comp.show = self.director.questions[self.scene_name]

        self.all_objects.update(delta)

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.archivist.talk_rect, 1)
        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blue4'), self.archive_comp.interact_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))




class Jail(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Jail'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.jail_tmx)
        self.map_bounding_box = pygame.Rect(5*TS-1, 0, 5*TS+1, BB_GROUND)

        self.left_ladder = objects.Ladder(self, Vector2(6*TS, 3*TS))
        self.all_objects.add(self.left_ladder)
        self.layered_sprites.add(self.left_ladder)

        self.right_ladder = objects.Ladder(self, Vector2(9*TS, 3*TS))
        self.all_objects.add(self.right_ladder)
        self.layered_sprites.add(self.right_ladder)

        self.door_to_corridor = objects.Door(self, Vector2(7*TS, 5*TS), 'Jail', 'Corridor')
        self.all_objects.add(self.door_to_corridor)
        self.layered_sprites.add(self.door_to_corridor)

        self.lawyer = objects.NPC(self, Vector2(7*TS, 3*TS), 'blue_cop', 'lawyer', pygame.Rect(7*TS, 2*TS, 2*TS, 2*TS), None, Vector2(8*TS, 3*TS), 45)
        self.all_objects.add(self.lawyer)
        self.layered_sprites.add(self.lawyer)

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 11*TS), Vector2(0, -1))

        cond = objects.ParticleEmitter(self, Vector2(TS*5+TS/2, TS/2))
        cond2 = objects.ParticleEmitter(self, Vector2(TS*9+TS/2, TS/2))
        self.cond_group = [cond, cond2]

        self.q_L_U = objects.FloatingImage(self, Vector2(2*TS+TS/2, 2*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_L_U)
        self.layered_sprites.add(self.q_L_U)

        self.q_R_U = objects.FloatingImage(self, Vector2(12*TS+TS/2, 2*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_R_U)
        self.layered_sprites.add(self.q_R_U)

        self.q_L_D = objects.FloatingImage(self, Vector2(2*TS+TS/2, 5*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_L_D)
        self.layered_sprites.add(self.q_L_D)

        self.q_R_D = objects.FloatingImage(self, Vector2(12*TS+TS/2, 5*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_R_D)
        self.layered_sprites.add(self.q_R_D)


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        if 'cut_scene' in list(transitionto_args.keys()):
            self.director.cut_scene = transitionto_args['cut_scene']
            self.top_black.show = False
            self.bottom_black.show = False

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        if self.director.current_thought not in ('win1', 'win2'):
            if self.director.curr_ikit_npcs != None:
                if self.director.first_ikit_made:
                    self.director.current_thought = '1st_jail_w/susp'
                else:
                    self.director.current_thought = 'jail_w/susp'
        self.dialogue_box.show_thoughts(self.director.current_thought)

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        for c in self.cond_group:
            c.update(delta)

        self.q_L_U.show = self.director.questions['Jail'][0]
        self.q_R_U.show = self.director.questions['Jail'][1]
        self.q_L_D.show = self.director.questions['Jail'][2]
        self.q_R_D.show = self.director.questions['Jail'][3]

        self.all_objects.update(delta)

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.lawyer.talk_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))




class Office(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Office'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.office_tmx)
        self.map_bounding_box = pygame.Rect(-2*TS-1, 0, 15*TS+1, BB_GROUND)

        self.passage_to_corridor = objects.Passage(self, Vector2(-TS, 5*TS), 'Office', 'Corridor', Vector2(-1, 0))
        self.all_objects.add(self.passage_to_corridor)
        self.layered_sprites.add(self.passage_to_corridor)

        self.cop1 = objects.NPC(self, Vector2(2*TS, 5*TS), 'blue_cop', 'cop1', pygame.Rect(TS, 5*TS, 3*TS, 2*TS))
        self.all_objects.add(self.cop1)
        self.layered_sprites.add(self.cop1)

        self.cop2 = objects.NPC(self, Vector2(6*TS, 5*TS), 'blue_cop', 'cop2', pygame.Rect(5*TS, 5*TS, 3*TS, 2*TS))
        self.all_objects.add(self.cop2)
        self.layered_sprites.add(self.cop2)

        self.player_comp = objects.InteractionObject(self, Vector2(11*TS, 6*TS), (2*TS, TS), pygame.Rect(11*TS, 6*TS, 2*TS, TS),
                                                     'player_comp', self.scene_name, True, 'PlayerCompIdentikit')
        self.all_objects.add(self.player_comp)
        self.layered_sprites.add(self.player_comp)

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 11*TS), Vector2(0, -1))

        cond = objects.ParticleEmitter(self, Vector2(TS*5+TS/2, TS/2))
        cond2 = objects.ParticleEmitter(self, Vector2(TS*9+TS/2, TS/2))
        self.cond_group = [cond, cond2]

        self.q_your_comp = objects.FloatingImage(self, Vector2(11*TS+TS/2, 4*TS-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_your_comp)
        self.layered_sprites.add(self.q_your_comp)


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        if 'cut_scene' in list(transitionto_args.keys()):
            self.director.cut_scene = transitionto_args['cut_scene']

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        self.dialogue_box.show_thoughts(self.director.current_thought)

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        for c in self.cond_group:
            c.update(delta)

        self.q_your_comp.show = self.director.questions[self.scene_name]

        self.all_objects.update(delta)

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.cop1.talk_rect, 1)
        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.cop2.talk_rect, 1)
        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blue4'), self.player_comp.interact_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))





class Entrance(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Entrance'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)
        self.dialogue_box = objects.DialogueBox(self, Vector2(TS, TS*11))

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.entrance_tmx)
        self.map_bounding_box = pygame.Rect(-2*TS-1, 0, 16*TS+1, BB_GROUND)

        self.passage_to_corridor = objects.Passage(self, Vector2(-TS, 5*TS), 'Entrance', 'Corridor', Vector2(-1, 0))
        self.all_objects.add(self.passage_to_corridor)
        self.layered_sprites.add(self.passage_to_corridor)

        self.passage_from_start = objects.Passage(self, Vector2(15*TS, 5*TS), 'Start', 'Entrance', Vector2(1, 0))
        self.all_objects.add(self.passage_from_start)
        self.layered_sprites.add(self.passage_from_start)

        self.dutyofficer = objects.NPC(self, Vector2(3*TS, 5*TS), 'blue_cop', 'dutyofficer', pygame.Rect(2*TS, 5*TS, 3*TS, 2*TS))
        self.all_objects.add(self.dutyofficer)
        self.layered_sprites.add(self.dutyofficer)

        self.closing_door = objects.ClosingDoor(self, Vector2(TS*15, TS*3))

        self.top_black = objects.CutSceneBlackBox(self, Vector2(0, -5*TS), Vector2(0, 1))
        self.bottom_black = objects.CutSceneBlackBox(self, Vector2(0, 11*TS), Vector2(0, -1))

        self.close_door = False

        cond = objects.ParticleEmitter(self, Vector2(TS*7+TS/2, TS/2))
        self.cond_group = [cond]

        self.q_dutyofficer = objects.FloatingImage(self, Vector2(TS*3, TS*4-TS/2), self.assets.floating_question)
        self.all_objects.add(self.q_dutyofficer)
        self.layered_sprites.add(self.q_dutyofficer)


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        # Start game sequence
        if 'close_door' in list(transitionto_args.keys()):
            self.close_door = transitionto_args['close_door']
        if 'thought' in list(transitionto_args.keys()):
            self.director.current_thought = transitionto_args['thought']
        if 'start_scene' in list(transitionto_args.keys()):
            self.director.start_scene = transitionto_args['start_scene']

        if self.director.player_go_door:
            self.director.player_go_door = False

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        if self.director.witness_to_add != None:
            self.all_objects.add(self.director.witness_to_add)
            self.layered_sprites.add(self.director.witness_to_add)

        self.dialogue_box.show_thoughts(self.director.current_thought)

        for c in self.cond_group:
            c.emit_start = True

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        for c in self.cond_group:
            c.update(delta)

        self.q_dutyofficer.show = self.director.questions[self.scene_name]

        self.all_objects.update(delta)

        self.closing_door.update()

        self.top_black.update()
        self.bottom_black.update()

        self.text_helper.update()
        self.dialogue_box.update()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.closing_door.render(main_surface)

        self.tilemap.render_map(main_surface)

        for c in self.cond_group:
            c.render(main_surface)

        self.layered_sprites.draw(main_surface)

        self.text_helper.render(main_surface)

        self.top_black.render(main_surface)
        self.bottom_black.render(main_surface)

        self.dialogue_box.render(main_surface)

        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('white'), self.map_bounding_box, 1)
        if DEBUG: pygame.draw.rect(main_surface, pygame.Color('blueviolet'), self.dutyofficer.talk_rect, 1)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(TS, TS*16), 'right':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))








class SearchInArchive(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'SearchInArchive'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.searchinarch_tmx)

        part_locs = [Vector2(TS*5, TS*3), Vector2(TS*5, TS*7), Vector2(TS*5, TS*3), Vector2(TS*5, TS*8)]
        self.identikit = objects.Identikit(self, part_locs)
        self.layered_sprites.change_layer(self.identikit.upper_part, 3)
        self.layered_sprites.change_layer(self.identikit.lower_part, 3)
        self.layered_sprites.change_layer(self.identikit.hair_part, 4)
        self.layered_sprites.change_layer(self.identikit.facial_hair_part, 4)

        self.identikit_selected = objects.Identikit(self, part_locs, False, False)
        self.layered_sprites.change_layer(self.identikit_selected.upper_part, 1)
        self.layered_sprites.change_layer(self.identikit_selected.lower_part, 1)
        self.layered_sprites.change_layer(self.identikit_selected.hair_part, 3)
        self.layered_sprites.change_layer(self.identikit_selected.facial_hair_part, 3)
        self.identikit_selected.clean_parts()

        self.case_hint = objects.UIHint(self, Vector2(TS*2, TS*14))

        self.left_arrow = objects.UIArrow(self, Vector2(0, TS*8), ['L', 'R'])
        self.all_objects.add(self.left_arrow)
        self.layered_sprites.add(self.left_arrow)

        self.right_arrow = objects.UIArrow(self, Vector2(TS*15, TS*8), ['R', 'L'])
        self.all_objects.add(self.right_arrow)
        self.layered_sprites.add(self.right_arrow)

        self.ident_part_pointer = objects.UIArrow(self, Vector2(TS*10, TS*13), ['l_D', 'l_U'])
        self.ident_part_pointer.show = True
        self.all_objects.add(self.ident_part_pointer)
        self.layered_sprites.add(self.ident_part_pointer)

        self.dot_upper = objects.UISelect(self, Vector2(TS*10, TS*14))
        self.all_objects.add(self.dot_upper)
        self.layered_sprites.add(self.dot_upper)

        self.dot_lower = objects.UISelect(self, Vector2(TS*11, TS*14))
        self.all_objects.add(self.dot_lower)
        self.layered_sprites.add(self.dot_lower)

        self.dot_hair = objects.UISelect(self, Vector2(TS*12, TS*14))
        self.all_objects.add(self.dot_hair)
        self.layered_sprites.add(self.dot_hair)

        self.dot_facial_hair = objects.UISelect(self, Vector2(TS*13, TS*14))
        self.all_objects.add(self.dot_facial_hair)
        self.layered_sprites.add(self.dot_facial_hair)

        self.prev_scene_name = 'Archive'
        self.show_arrow_timer = 0

        self.show_cheat = 0

        self.cond_group = None



    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        self.prev_scene_player_pos = transitionto_args['player_pos']
        self.prev_scene_player_facing = transitionto_args['player_facing']

        self.identikit.set_cases(self.assets.archive_cases)
        self.identikit_selected.set_cases(self.assets.archive_cases)
        self.case_hint.set_hint([self.identikit.cases[self.identikit.case_idx]['assigned_hint']])

        self.identikit.clean_parts()
        self.identikit_selected.clean_parts()

        self.dot_upper.show = False
        self.dot_lower.show = False
        self.dot_hair.show = False
        self.dot_facial_hair.show = False

        for ip in list(self.director.investigated_main_hints.keys()):
            if self.director.investigated_main_hints[ip] != None:
                if ip == 'upper':
                    self.dot_upper.locked = True
                    self.dot_upper.show = True
                    self.identikit_selected.set_ikit_part('upper', self.director.investigated_main_hints['upper']['ikit_part_num'])
                elif ip == 'lower':
                    self.dot_lower.locked = True
                    self.dot_lower.show = True
                    self.identikit_selected.set_ikit_part('lower', self.director.investigated_main_hints['lower']['ikit_part_num'])
                elif ip == 'hair':
                    self.dot_hair.locked = True
                    self.dot_hair.show = True
                    self.identikit_selected.set_ikit_part('hair', self.director.investigated_main_hints['hair']['ikit_part_num'])
                elif ip == 'facial_hair':
                    self.dot_facial_hair.locked = True
                    self.dot_facial_hair.show = True
                    self.identikit_selected.set_ikit_part('facial_hair', self.director.investigated_main_hints['facial_hair']['ikit_part_num'])

        self.identikit.change_parts()

        self.director.cut_scene = False

        self.confirm_button = False
        self.quit_button = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        pressed = pygame.key.get_pressed()
        self.show_cheat = pressed[pygame.K_F12]

        cur_case = self.identikit.cases[self.identikit.case_idx]

        if self.fade.finished_out:
            if self.confirm_button or self.quit_button:
                if DEBUG: print('CHANGE SCENE')
                args_dict = {'cut_scene': False,
                             'player_pos': self.prev_scene_player_pos,
                             'player_facing': self.prev_scene_player_facing}

                ikit_try = self.identikit_selected.get_parts_numbers()

                if self.confirm_button:
                    if ikit_try != settings.IKIT_ZERO:
                        if len(self.director.investigated_clues) == 1:
                            if DEBUG: print('A-case_given-confirm-1st_ikit')
                            self.director.current_thought = '1st_ikit'
                            self.director.player_indicator = 'try_ikit'
                            self.director.first_ikit_try = True
                        else:
                            if DEBUG: print('A-case_given-confirm-new_ikit')
                            self.director.current_thought = 'new_ikit'
                            self.director.player_indicator = 'try_ikit'
                            self.director.first_ikit_try = False

                        self.director.questions['Corridor'][0] = False
                        self.director.questions['Corridor'][2] = True
                        self.director.questions['Archive'] = False
                        self.director.questions['Office'] = True
                        self.director.questions['Entrance'] = False
                    else:
                        self.director.player_indicator = None

                if self.quit_button:
                    ikit_try = settings.IKIT_ZERO
                    self.director.player_indicator = None
                    # Очистить натыканный фоторобот по выходу
                    self.identikit_selected.clean_parts()

                self.director.ikit_try = ikit_try

                self.director.go_to(self.prev_scene_name, args_dict)
                return

        if self.key_control.left:
            self.show_arrow_timer = SHOW_ARROW_DURATION
            self.left_arrow.show = True
            self.assets.sounds['scroll'].play()
            if DEBUG: print('SHOW < ARROW')
            if DEBUG: print('press left-cur_case:', cur_case, self.identikit.case_idx)

        if self.key_control.right:
            self.show_arrow_timer = SHOW_ARROW_DURATION
            self.right_arrow.show = True
            self.assets.sounds['scroll'].play()
            if DEBUG: print('SHOW > ARROW')
            if DEBUG: print('press right-cur_case:', cur_case, self.identikit.case_idx)

        if self.key_control.up:
            # UIDots show
            if cur_case['ikit_part'] == 'upper':
                if not self.dot_upper.locked:
                    self.dot_upper.show = False
                    self.identikit_selected.set_ikit_part('upper', 0)
            elif cur_case['ikit_part'] == 'lower':
                if not self.dot_lower.locked:
                    self.dot_lower.show = False
                    self.identikit_selected.set_ikit_part('lower', 0)
            elif cur_case['ikit_part'] == 'hair':
                if not self.dot_hair.locked:
                    self.dot_hair.show = False
                    self.identikit_selected.set_ikit_part('hair', 0)
            elif cur_case['ikit_part'] == 'facial_hair':
                if not self.dot_facial_hair.locked:
                    self.dot_facial_hair.show = False
                    self.identikit_selected.set_ikit_part('facial_hair', 0)

            self.key_control.clear_keys()

            self.show_arrow_timer = SHOW_ARROW_DURATION
            self.ident_part_pointer.show_opposite = True
            if DEBUG: print('RETURN CASE TO ACASES', cur_case['ikit_part'], cur_case['ikit_part_num'])
            if DEBUG: print(self.identikit_selected.get_parts_numbers())

        if self.key_control.down:
            # UIDots switch
            setted = self.identikit_selected.get_parts_numbers()
            if setted[cur_case['ikit_part']] != cur_case['ikit_part_num']:
                if cur_case['ikit_part_num'] != 0:
                    if cur_case['ikit_part'] == 'upper':
                        if not self.dot_upper.locked:
                            self.identikit_selected.set_ikit_part('upper', cur_case['ikit_part_num'])
                            if not self.dot_upper.show:
                                self.dot_upper.show = True
                            else:
                                self.dot_upper.switch = True
                    elif cur_case['ikit_part'] == 'lower':
                        if not self.dot_lower.locked:
                            self.identikit_selected.set_ikit_part('lower', cur_case['ikit_part_num'])
                            if not self.dot_lower.show:
                                self.dot_lower.show = True
                            else:
                                self.dot_lower.switch = True
                    elif cur_case['ikit_part'] == 'hair':
                        if not self.dot_hair.locked:
                            self.identikit_selected.set_ikit_part('hair', cur_case['ikit_part_num'])
                            if not self.dot_hair.show:
                                self.dot_hair.show = True
                            else:
                                self.dot_hair.switch = True
                    elif cur_case['ikit_part'] == 'facial_hair':
                        if not self.dot_facial_hair.locked:
                            self.identikit_selected.set_ikit_part('facial_hair', cur_case['ikit_part_num'])
                            if not self.dot_facial_hair.show:
                                self.dot_facial_hair.show = True
                            else:
                                self.dot_facial_hair.switch = True

            self.assets.sounds['chick'].play()
            self.key_control.clear_keys()
            if DEBUG: print('TAKE CASE IDENTIKIT PART:', cur_case['ikit_part'], cur_case['ikit_part_num'])
            if DEBUG: print(self.identikit_selected.get_parts_numbers())

        if self.key_control.x:
            if not self.confirm_button and not self.quit_button:
                if DEBUG: print('TRY')
                self.confirm_button = True
                self.quit_button = False
                self.assets.sounds['confirm'].play()
                # Включить фейдаут сцены
                self.fade.fade_out()
                self.director.cut_scene = True
                self.key_control.clear_keys()

        if self.key_control.z:
            if not self.confirm_button and not self.quit_button:
                if DEBUG: print('JUST QUIT')
                self.confirm_button = False
                self.quit_button = True
                self.assets.sounds['confirm'].play()
                # Включить фейдаут сцены
                self.fade.fade_out()
                self.director.cut_scene = True
                self.key_control.clear_keys()

        self.case_hint.update()
        self.identikit.update()
        self.identikit_selected.update()

        if cur_case['ikit_part'] == 'upper':
            self.ident_part_pointer.set_pos(Vector2(TS*10, TS*13))
        elif cur_case['ikit_part'] == 'lower':
            self.ident_part_pointer.set_pos(Vector2(TS*11, TS*13))
        elif cur_case['ikit_part'] == 'hair':
            self.ident_part_pointer.set_pos(Vector2(TS*12, TS*13))
        elif cur_case['ikit_part'] == 'facial_hair':
            self.ident_part_pointer.set_pos(Vector2(TS*13, TS*13))

        self.all_objects.update(delta)

        if self.show_arrow_timer >= 0:
            self.show_arrow_timer -= 1

            if self.show_arrow_timer == 0:
                self.left_arrow.show = False
                self.right_arrow.show = False
                self.ident_part_pointer.show_opposite = False

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        # Номера/имена дел в Archive
        t1 = text_mono.render_text(self.identikit.cases[self.identikit.case_idx]['case'], self.assets.tile_font, 1)
        t1_rect = t1.get_rect(topleft = Vector2(TS*7, 0))
        main_surface.blit(t1, t1_rect)

        self.tilemap.render_map(main_surface)

        self.layered_sprites.draw(main_surface)

        self.case_hint.render(main_surface)

        # PICO8 symbols подсказки кнопок
        locs = {'left':Vector2(0, TS*4), 'right':Vector2(TS*15, TS*4), 'up':Vector2(TS*15, TS*13), 'down':Vector2(TS*15, TS*14),
                'quit':Vector2(TS, TS*16), 'try':Vector2(TS*11, TS*16),
                'caseN':Vector2(TS, 0), 'susp':Vector2(TS*4, TS), 'ikit':Vector2(TS*3, TS*2),
                'hint':Vector2(TS*2, TS*13)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.show_cheat:
            main_surface.blit(self.assets.cheat_image, (0, 0))

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))







class PlayerCompIdentikit(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'PlayerCompIdentikit'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.playercomp_ikit_tmx)

        part_locs = [Vector2(TS*5, TS*5), Vector2(TS*5, TS*9), Vector2(TS*5, TS*5), Vector2(TS*5, TS*10)]
        self.identikit = objects.Identikit(self, part_locs, False, False)
        self.layered_sprites.change_layer(self.identikit.upper_part, 3)
        self.layered_sprites.change_layer(self.identikit.lower_part, 3)
        self.layered_sprites.change_layer(self.identikit.hair_part, 4)
        self.layered_sprites.change_layer(self.identikit.facial_hair_part, 4)

        self.selected_ikit_hints = objects.UIHint(self, Vector2(TS*8, TS))

        self.dot_upper = objects.UISelect(self, Vector2(TS*7, TS))
        self.dot_upper.locked = True
        self.dot_upper.show = False
        self.all_objects.add(self.dot_upper)
        self.layered_sprites.add(self.dot_upper)

        self.dot_lower = objects.UISelect(self, Vector2(TS*7, TS*2))
        self.dot_lower.locked = True
        self.dot_lower.show = False
        self.all_objects.add(self.dot_lower)
        self.layered_sprites.add(self.dot_lower)

        self.dot_hair = objects.UISelect(self, Vector2(TS*7, TS*3))
        self.dot_hair.locked = True
        self.dot_hair.show = False
        self.all_objects.add(self.dot_hair)
        self.layered_sprites.add(self.dot_hair)

        self.dot_facial_hair = objects.UISelect(self, Vector2(TS*7, TS*4))
        self.dot_facial_hair.locked = True
        self.dot_facial_hair.show = False
        self.all_objects.add(self.dot_facial_hair)
        self.layered_sprites.add(self.dot_facial_hair)

        self.prev_scene_name = 'Office'
        self.show_arrow_timer = 0

        self.show_cheat = 0

        self.cond_group = None


    def construct_selected_hints(self, selected_ikit, invest_main_hints):
        ikit_hint = []

        if invest_main_hints['upper'] != None:
            ikit_hint.append(invest_main_hints['upper']['assigned_hint'])
        else:
            if selected_ikit['upper'] == self.assets.true_crim_ip_num[0]:
                ikit_hint.append(self.assets.true_criminal[0]['assigned_hint'])
            else:
                if selected_ikit['upper'] == 0:
                    ikit_hint.append([])
                else:
                    for fp in self.assets.false_suspects_parts['upper']:
                        if fp['ikit_part_num'] == selected_ikit['upper']:
                            print('fp', fp)
                            ikit_hint.append(fp['assigned_hint'])
                            break

        if invest_main_hints['lower'] != None:
            ikit_hint.append(invest_main_hints['lower']['assigned_hint'])
        else:
            if selected_ikit['lower'] == self.assets.true_crim_ip_num[1]:
                ikit_hint.append(self.assets.true_criminal[1]['assigned_hint'])
            else:
                if selected_ikit['lower'] == 0:
                    ikit_hint.append([])
                else:
                    for fp in self.assets.false_suspects_parts['lower']:
                        if fp['ikit_part_num'] == selected_ikit['lower']:
                            print('fp', fp)
                            ikit_hint.append(fp['assigned_hint'])
                            break

        if invest_main_hints['hair'] != None:
            ikit_hint.append(invest_main_hints['hair']['assigned_hint'])
        else:
            if selected_ikit['hair'] == self.assets.true_crim_ip_num[2]:
                ikit_hint.append(self.assets.true_criminal[2]['assigned_hint'])
            else:
                if selected_ikit['hair'] == 0:
                    ikit_hint.append([])
                else:
                    for fp in self.assets.false_suspects_parts['hair']:
                        if fp['ikit_part_num'] == selected_ikit['hair']:
                            print('fp', fp)
                            ikit_hint.append(fp['assigned_hint'])
                            break

        if invest_main_hints['facial_hair'] != None:
            ikit_hint.append(invest_main_hints['facial_hair']['assigned_hint'])
        else:
            if selected_ikit['facial_hair'] == self.assets.true_crim_ip_num[3]:
                ikit_hint.append(self.assets.true_criminal[3]['assigned_hint'])
            else:
                if selected_ikit['facial_hair'] == 0:
                    ikit_hint.append([])
                else:
                    for fp in self.assets.false_suspects_parts['facial_hair']:
                        if fp['ikit_part_num'] == selected_ikit['facial_hair']:
                            print('fp', fp)
                            ikit_hint.append(fp['assigned_hint'])
                            break

        if DEBUG: print('IKIT hint:', ikit_hint)
        # self.selected_ikit_hints.set_hint(ikit_hint)
        return ikit_hint



    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        self.identikit.set_cases(self.assets.archive_cases)

        self.identikit.clean_parts()

        self.prev_scene_player_pos = transitionto_args['player_pos']
        self.prev_scene_player_facing = transitionto_args['player_facing']

        # установить уже исследованные главные подсказки
        for ip in list(self.director.investigated_main_hints.keys()):
            if self.director.investigated_main_hints[ip] != None:
                if ip == 'upper':
                    self.dot_upper.show = True
                    self.identikit.set_ikit_part('upper', self.director.investigated_main_hints['upper']['ikit_part_num'])
                elif ip == 'lower':
                    self.dot_lower.show = True
                    self.identikit.set_ikit_part('lower', self.director.investigated_main_hints['lower']['ikit_part_num'])
                elif ip == 'hair':
                    self.dot_hair.show = True
                    self.identikit.set_ikit_part('hair', self.director.investigated_main_hints['hair']['ikit_part_num'])
                elif ip == 'facial_hair':
                    self.dot_facial_hair.show = True
                    self.identikit.set_ikit_part('facial_hair', self.director.investigated_main_hints['facial_hair']['ikit_part_num'])
            else:
                if ip == 'upper':
                    self.identikit.set_ikit_part('upper', self.director.ikit_try['upper'])
                elif ip == 'lower':
                    self.identikit.set_ikit_part('lower', self.director.ikit_try['lower'])
                elif ip == 'hair':
                    self.identikit.set_ikit_part('hair', self.director.ikit_try['hair'])
                elif ip == 'facial_hair':
                    self.identikit.set_ikit_part('facial_hair', self.director.ikit_try['facial_hair'])

        selected_ip = self.construct_selected_hints(self.director.ikit_try, self.director.investigated_main_hints)
        self.selected_ikit_hints.set_hint(selected_ip)

        self.confirm_button = False
        self.quit_button = False
        self.to_todo = False

        self.director.cut_scene = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        pressed = pygame.key.get_pressed()
        self.show_cheat = pressed[pygame.K_F12]

        if self.fade.finished_out:
            if self.confirm_button or self.quit_button:
                if DEBUG: print('CHANGE SCENE ({})'.format(self.__class__.__name__))
                args_dict = {'cut_scene': False,
                             'player_pos': self.prev_scene_player_pos,
                             'player_facing': self.prev_scene_player_facing}

                print(args_dict)

                ikit_made = self.identikit.get_parts_numbers()

                if self.confirm_button:
                    if ikit_made != settings.IKIT_ZERO:
                        if len(self.director.investigated_clues) == 1:
                            if DEBUG: print('A-case_given-confirm-1st_made_ikit')
                            self.director.current_thought = '1st_made_ikit'
                            self.director.player_indicator = 'made_ikit'
                            self.director.first_ikit_made = True
                        else:
                            if DEBUG: print('A-case_given-confirm-made_ikit')
                            self.director.current_thought = 'made_ikit'
                            self.director.player_indicator = 'made_ikit'
                            self.director.first_ikit_made = False

                        self.director.questions['Corridor'][0] = False
                        self.director.questions['Corridor'][2] = False
                        self.director.questions['Office'] = False
                        self.director.questions['Archive'] = False
                        self.director.questions['Entrance'] = True

                if self.quit_button:
                    ikit_made = settings.IKIT_ZERO

                self.director.ikit_made = ikit_made

                self.director.go_to(self.prev_scene_name, args_dict)
                return

            if self.to_todo:
                if DEBUG: print('CHANGE SCENE ({})'.format(self.__class__.__name__))
                args_dict = {'cut_scene': False,
                             'player_pos': self.prev_scene_player_pos,
                             'player_facing': self.prev_scene_player_facing}

                self.director.go_to('PlayerCompTodolist', args_dict)
                return

        if self.key_control.right:
            self.to_todo = True
            self.assets.sounds['scroll'].play()
            # Включить фейдаут сцены
            self.fade.fade_out()
            self.director.cut_scene = True
            self.key_control.clear_keys()


        if self.key_control.x:
            if not self.confirm_button and not self.quit_button:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.confirm_button = True
                self.quit_button = False
                self.assets.sounds['confirm'].play()
                # Включить фейдаут сцены
                self.fade.fade_out()
                self.director.cut_scene = True
                self.key_control.clear_keys()

        if self.key_control.z:
            if not self.confirm_button and not self.quit_button:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.confirm_button = False
                self.quit_button = True
                self.assets.sounds['confirm'].play()
                # Включить фейдаут сцены
                self.fade.fade_out()
                self.director.cut_scene = True
                self.key_control.clear_keys()

        self.identikit.update()

        self.all_objects.update(delta)

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        self.layered_sprites.draw(main_surface)

        self.selected_ikit_hints.render(main_surface)

        # Investigated case clues
        if self.director.case_given:
            for x, clue in enumerate(self.director.investigated_clues):
                main_surface.blit(self.assets.clues_icons[clue], (TS*8+TS*x, 0))

        main_surface.blit(text_mono.render_text(str(len(self.director.investigated_clues)), self.assets.tile_font, 1), Vector2(TS*13, 0))

        # PICO8 symbols подсказки кнопок
        locs = {'quit':Vector2(TS, TS*16), 'make':Vector2(TS*10, TS*16), '2':Vector2(TS*8, TS*16),
                'case':Vector2(TS, 0), 'hints':Vector2(TS, TS), '/4':Vector2(TS*14, 0)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.show_cheat:
            main_surface.blit(self.assets.cheat_image, (0, 0))

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))





class PlayerCompTodolist(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'PlayerCompTodolist'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.playercomp_todo_tmx)

        self.todosurf_pos = Vector2(0, TS*3)
        self.todosurf_shift = Vector2(0, 0)
        self.render_window = Vector2(15, 10) # tiles

        self.top_arrow = objects.UIArrow(self, Vector2(TS*7, TS), ['U', 'D'])
        self.all_objects.add(self.top_arrow)
        self.layered_sprites.add(self.top_arrow)

        self.bottom_arrow = objects.UIArrow(self, Vector2(TS*7, TS*14), ['D', 'U'])
        self.all_objects.add(self.bottom_arrow)
        self.layered_sprites.add(self.bottom_arrow)

        self.show_arrow_timer = 0

        self.cond_group = None


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        self.prev_scene_player_pos = transitionto_args['player_pos']
        self.prev_scene_player_facing = transitionto_args['player_facing']

        self.to_ikit = False

        self.director.cut_scene = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        self.all_objects.update(delta)

        if self.fade.finished_out:
            if self.to_ikit:
                if DEBUG: print('CHANGE SCENE ({})'.format(self.__class__.__name__))
                args_dict = {'cut_scene': False,
                             'player_pos': self.prev_scene_player_pos,
                             'player_facing': self.prev_scene_player_facing}

                self.director.go_to('PlayerCompIdentikit', args_dict)
                return

        if self.key_control.left:
            self.to_ikit = True
            self.assets.sounds['scroll'].play()
            # Включить фейдаут сцены
            self.fade.fade_out()
            self.director.cut_scene = True
            self.key_control.clear_keys()

        if self.key_control.up:
            self.show_arrow_timer = SHOW_ARROW_DURATION
            self.top_arrow.show = True

            if self.todosurf_shift.y > 0:
                if DEBUG: print('TODOLIST ^')
                self.todosurf_shift.y -= 1
                self.assets.sounds['scroll'].play()
                self.key_control.clear_keys()

        if self.key_control.down:
            self.show_arrow_timer = SHOW_ARROW_DURATION
            self.bottom_arrow.show = True

            if self.todosurf_shift.y < (self.assets.todolist_surf.get_height()//TS)-self.render_window.y:
                if DEBUG: print('TODOLIST  V')
                self.todosurf_shift.y += 1
                self.assets.sounds['scroll'].play()
                self.key_control.clear_keys()

        if self.show_arrow_timer >= 0:
            self.show_arrow_timer -= 1

            if self.show_arrow_timer == 0:
                self.top_arrow.show = False
                self.bottom_arrow.show = False

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        self.layered_sprites.draw(main_surface)

        # Рендер картинки в рект
        if (self.assets.todolist_surf.get_height()//TS) > self.render_window.y:
            subsurface = self.assets.todolist_surf.subsurface(pygame.Rect(0, TS*self.todosurf_shift.y, TS*self.render_window.x, TS*self.render_window.y))
        else:
            subsurface = self.assets.todolist_surf.subsurface(pygame.Rect(0, TS*self.todosurf_shift.y, TS*self.render_window.x, TS*(self.assets.todolist_surf.get_height()//TS)))

        main_surface.blit(subsurface, self.todosurf_pos)

        if (self.assets.todolist_surf.get_height()//TS) > self.render_window.y:
            if self.todosurf_shift.y > 0:
                main_surface.blit(self.assets.labels['up'], (TS*15, TS*2))
            if self.todosurf_shift.y < (self.assets.todolist_surf.get_height()//TS)-self.render_window.y:
                main_surface.blit(self.assets.labels['down'], (TS*15, TS*14))

        # PICO8 symbols подсказки кнопок
        locs = {'1':Vector2(TS*7, TS*16), 'mytodo':Vector2(TS, 0)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))







class Interrogation(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Interrogation'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.interrogation_tmx)

        part_locs = [Vector2(TS*5, 0), Vector2(TS*5, TS*4), Vector2(TS*5, 0), Vector2(TS*5, TS*5)]
        self.identikit = objects.Identikit(self, part_locs, False, False)
        self.layered_sprites.change_layer(self.identikit.upper_part, 3)
        self.layered_sprites.change_layer(self.identikit.lower_part, 3)
        self.layered_sprites.change_layer(self.identikit.hair_part, 4)
        self.layered_sprites.change_layer(self.identikit.facial_hair_part, 4)

        self.hint1 = objects.UIHint(self, Vector2(TS*3, TS*11))
        self.hint2 = objects.UIHint(self, Vector2(TS*3, TS*12))
        self.hint3 = objects.UIHint(self, Vector2(TS*3, TS*13))
        self.hint4 = objects.UIHint(self, Vector2(TS*3, TS*14))

        self.answ1 = objects.UIAnswer(self, Vector2(TS*8, TS*11))
        self.answ2 = objects.UIAnswer(self, Vector2(TS*8, TS*12))
        self.answ3 = objects.UIAnswer(self, Vector2(TS*8, TS*13))
        self.answ4 = objects.UIAnswer(self, Vector2(TS*8, TS*14))
        self.layered_sprites.add(self.answ1)
        self.layered_sprites.add(self.answ2)
        self.layered_sprites.add(self.answ3)
        self.layered_sprites.add(self.answ4)

        self.ikit_part_pointer = objects.UIArrow(self, Vector2(self.answ1.pos.x-TS*3, self.answ1.pos.y), ['l_R', 'l_L'])
        self.ikit_part_pointer.show = True
        self.all_objects.add(self.ikit_part_pointer)
        self.layered_sprites.add(self.ikit_part_pointer)

        self.prev_scene_name = 'Jail'
        self.show_arrow_timer = 0

        self.show_cheat = 0

        self.cond_group = None


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        self.prev_scene_player_pos = transitionto_args['player_pos']
        self.prev_scene_player_facing = transitionto_args['player_facing']

        self.identikit.set_cases(self.assets.archive_cases)

        self.criminal_ips = transitionto_args['criminal_parts']
        self.identikit.set_ikit_part('upper', self.criminal_ips[0]['ikit_part_num'])
        self.identikit.set_ikit_part('lower', self.criminal_ips[1]['ikit_part_num'])
        self.identikit.set_ikit_part('hair', self.criminal_ips[2]['ikit_part_num'])
        self.identikit.set_ikit_part('facial_hair', self.criminal_ips[3]['ikit_part_num'])

        assig_hints = {'0':self.criminal_ips[0]['assigned_hint'].copy(),'1':self.criminal_ips[1]['assigned_hint'].copy(),
                       '2':self.criminal_ips[2]['assigned_hint'].copy(),'3':self.criminal_ips[3]['assigned_hint'].copy()}
        self.rnd_ap_keys = list(assig_hints.keys())
        random.shuffle(self.rnd_ap_keys)
        print(self.rnd_ap_keys)
        self.hint1.set_hint([assig_hints[self.rnd_ap_keys[0]]])
        self.hint2.set_hint([assig_hints[self.rnd_ap_keys[1]]])
        self.hint3.set_hint([assig_hints[self.rnd_ap_keys[2]]])
        self.hint4.set_hint([assig_hints[self.rnd_ap_keys[3]]])

        self.answ1.set_answer(None)
        self.answ2.set_answer(None)
        self.answ3.set_answer(None)
        self.answ4.set_answer(None)

        self.selected_idx = 0
        self.selected_hint = self.hint1
        self.selected_answer = self.answ1

        self.hints_counter = 0
        self.interr_main_hints = {'upper':None,'lower':None,'hair':None,'facial_hair':None}
        self.win_approve = {'upper':False,'lower':False,'hair':False,'facial_hair':False}

        self.confirm_button = False
        self.allow_to_confirm = False

        self.director.cut_scene = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Pause/unpause game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEBUG: print('>> Game paused')
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.key_control.handle_key_events(event)


    def update(self, delta):
        if self.director.paused:
            if self.key_control.x:
                if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                self.director.quit()
                self.key_control.clear_keys()

            if self.key_control.z:
                if DEBUG: print('QUIT ({})'.format(self.__class__.__name__))
                self.director.paused = not self.director.paused
                self.key_control.clear_keys()
            return

        pressed = pygame.key.get_pressed()
        self.show_cheat = pressed[pygame.K_F12]

        if self.fade.finished_out:
            if self.confirm_button:
                if DEBUG: print('CHANGE SCENE ({})'.format(self.__class__.__name__))
                args_dict = {'cut_scene': False,
                             'player_pos': self.prev_scene_player_pos,
                             'player_facing': self.prev_scene_player_facing}

                # Добавить
                for tp in list(self.interr_main_hints.keys()):
                    part = self.interr_main_hints[tp]
                    if part != None:
                        clue = part['assigned_hint'][0]
                        if clue not in self.director.investigated_clues:
                             self.director.investigated_clues.append(clue)
                             # self.director.investigated_main_hints[tp] = part # интереснее, когда не добавляется подсказка напрямую
                        else:
                            if self.director.investigated_main_hints[tp] == None:
                                self.director.investigated_main_hints[tp] = part
                            else:
                                # Часть совпадает с true_criminal
                                self.win_approve[tp] = True

                if DEBUG: print('win approve:', list(self.win_approve.values()))
                if DEBUG: print('<!> Inv. main hints:', self.director.investigated_main_hints)
                if DEBUG: print('<!> Inv. main clues:', self.director.investigated_clues)

                if len(self.director.investigated_clues) == 4:
                    if DEBUG: print('<!> All clues investigated')
                    self.director.all_clues_investigated = True

                if all(list(self.director.investigated_main_hints.values())):
                    if DEBUG: print('<!> All main hints investigated')
                    self.director.all_hints_investigated = True

                # Проверка на то, что true_criminal найден
                if all(list(self.win_approve.values())):
                    self.director.true_criminal_finded = True

                # WIN
                if self.director.all_clues_investigated and self.director.all_hints_investigated:
                    if self.director.true_criminal_finded:
                        if DEBUG: print('YOU WIN THIS CASE!')
                        self.assets.sounds['win'].play()
                        self.director.case_given = False
                        self.director.current_thought = 'win1'
                        self.director.player_indicator = None

                        self.director.questions['BossBriefroom'] = True
                        self.director.questions['Corridor'][0] = False
                        self.director.questions['Corridor'][1] = False
                        self.director.questions['Corridor'][2] = False
                        self.director.questions['Entrance'] = False

                self.director.go_to(self.prev_scene_name, args_dict)
                return


        if self.key_control.right:
            if DEBUG: print('CHECK ?')
            ipart = self.criminal_ips[int(self.rnd_ap_keys[self.selected_idx])]
            ipart_keys = list(ipart.keys())
            # Правильная подсказка
            if 'mp_idx' in ipart_keys:
                if DEBUG: print(ipart['case'])
                self.interr_main_hints[ipart['ikit_part']] = ipart
                self.selected_answer.set_answer('yes', ipart['assigned_hint'])
                self.assets.sounds['yes_interr'].play()
            else:
                self.selected_answer.set_answer('no')
                self.assets.sounds['chick'].play()
            if not self.allow_to_confirm:
                self.allow_to_confirm = True
            self.key_control.clear_keys()

        if self.key_control.up:
            if DEBUG: print('SCROLL ^')
            self.selected_idx -= 1
            if self.selected_idx < 0:
                self.selected_idx = 3
            self.assets.sounds['scroll'].play()
            self.key_control.clear_keys()

        if self.key_control.down:
            if DEBUG: print('SCROLL V')
            self.selected_idx += 1
            if self.selected_idx > 3:
                self.selected_idx = 0
            self.assets.sounds['scroll'].play()
            self.key_control.clear_keys()

        if self.key_control.x:
            if self.allow_to_confirm:
                if not self.confirm_button:
                    if DEBUG: print('CONFIRM ({})'.format(self.__class__.__name__))
                    self.confirm_button = True
                    self.assets.sounds['confirm'].play()
                    # Включить фейдаут сцены
                    self.fade.fade_out()
                    self.director.cut_scene = True
                    self.key_control.clear_keys()

        self.identikit.update()

        if self.selected_idx == 0:
            self.selected_hint = self.hint1
            self.selected_answer = self.answ1
        if self.selected_idx == 1:
            self.selected_hint = self.hint2
            self.selected_answer = self.answ2
        if self.selected_idx == 2:
            self.selected_hint = self.hint3
            self.selected_answer = self.answ3
        if self.selected_idx == 3:
            self.selected_hint = self.hint4
            self.selected_answer = self.answ4
        self.ikit_part_pointer.set_pos(Vector2(self.selected_hint.pos.x-TS*3, self.selected_hint.pos.y))

        self.all_objects.update(delta)

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        self.layered_sprites.draw(main_surface)

        self.hint1.render(main_surface)
        self.hint2.render(main_surface)
        self.hint3.render(main_surface)
        self.hint4.render(main_surface)

        main_surface.blit(text_mono.render_text('?', self.assets.tile_font, 1), Vector2(TS*1, TS*11))
        main_surface.blit(text_mono.render_text('?', self.assets.tile_font, 1), Vector2(TS*1, TS*12))
        main_surface.blit(text_mono.render_text('?', self.assets.tile_font, 1), Vector2(TS*1, TS*13))
        main_surface.blit(text_mono.render_text('?', self.assets.tile_font, 1), Vector2(TS*1, TS*14))

        main_surface.blit(text_mono.render_text(':', self.assets.tile_font, 1), Vector2(TS*7, TS*11))
        main_surface.blit(text_mono.render_text(':', self.assets.tile_font, 1), Vector2(TS*7, TS*12))
        main_surface.blit(text_mono.render_text(':', self.assets.tile_font, 1), Vector2(TS*7, TS*13))
        main_surface.blit(text_mono.render_text(':', self.assets.tile_font, 1), Vector2(TS*7, TS*14))

        # PICO8 symbols подсказки кнопок
        locs = {'right':Vector2(TS, TS*16), 'up':Vector2(TS*15, TS*12), 'down':Vector2(TS*15, TS*13),
                'interr':Vector2(TS, 0)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        if self.allow_to_confirm:
            main_surface.blit(self.assets.labels['got_it'], Vector2(TS*9, TS*16))

        if self.show_cheat:
            main_surface.blit(self.assets.cheat_image, (0, 0))

        if self.director.paused:
            self.fade_surface.set_alpha(PAUSED_ALPHA)
        else:
            self.fade_surface.set_alpha(self.fade.alpha)
        main_surface.blit(self.fade_surface, Vector2(0, 0))

        if self.director.paused:
            main_surface.blit(self.assets.paused_surf, Vector2(TS, TS*6))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))













class Start(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Start'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.splash_fade = objects.SceneFadeInOut(FADEINOUT_DURATION_SPLASH)
        self.splash_fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        self.show_splash = True

        self.key_control = objects.KeyControl()

        self.text_helper = objects.TextHelper(self, self.assets.text_helpers)

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.tilemap = objects.TileMap(self.assets.start_tmx)
        self.map_bounding_box = pygame.Rect(2*TS-1, 0, 11*TS+1, BB_GROUND)

        self.left_ladder = objects.Ladder(self, Vector2(4*TS, 7*TS))
        self.all_objects.add(self.left_ladder)
        self.layered_sprites.add(self.left_ladder)

        self.right_ladder = objects.Ladder(self, Vector2(11*TS, 7*TS))
        self.all_objects.add(self.right_ladder)
        self.layered_sprites.add(self.right_ladder)

        self.door_to_entrance = objects.Door(self, Vector2(7*TS, 6*TS), 'Start', 'Entrance')
        self.all_objects.add(self.door_to_entrance)
        self.layered_sprites.add(self.door_to_entrance)

        self.q_start_door = objects.FloatingImage(self, Vector2(7*TS+TS/2, 5*TS-TS/2), self.assets.floating_question)
        self.q_start_door.show = True
        self.all_objects.add(self.q_start_door)
        self.layered_sprites.add(self.q_start_door)

        pygame.mixer.music.play(-1)

        self.cond_group = None

        # Splash image
        splash_tilemap = objects.TileMap(self.assets.splash_tmx, Vector2(0, 0))
        splash_surf = pygame.Surface((TS*16, TS*3))
        splash_surf.fill(pygame.Color('black'))
        splash_tilemap.render_map(splash_surf)
        splash_surf.blit(self.assets.start_labels[0], Vector2(0, TS))
        splash_surf.blit(self.assets.ip_selected_imgs['lens'], Vector2(TS*6, TS))
        splash_surf.blit(self.assets.start_labels[1], Vector2(TS*7, TS))

        self.splash_image = objects.FloatingImage(self, Vector2(0, TS*6), splash_surf, Vector2(0, TS))
        self.splash_image.show = True


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        player_pos = transitionto_args['player_pos']
        player_facing = transitionto_args['player_facing']

        self.player = objects.Player(self, player_pos, player_facing, self.assets.player_anim_set)
        self.all_objects.add(self.player)
        self.layered_sprites.add(self.player)

        self.player_indicator = objects.Indicator(self)
        self.all_objects.add(self.player_indicator)
        self.layered_sprites.add(self.player_indicator)
        self.player_indicator.set_item_type(self.director.player_indicator)

        self.director.cut_scene = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()

        self.splash_fade_surface.fill(pygame.Color('black'))


    def handle_events(self, events):
        for event in events:
            # Exit game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.director.quit()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if self.show_splash:
                    self.show_splash = False
                    self.splash_image.flow_to = True
                    self.splash_fade.fade_in()

                if not self.director.cut_scene:
                    self.player.key_control.handle_key_events(event)
                self.key_control.handle_key_events(event)


    def update(self, delta):
        self.all_objects.update(delta)
        self.splash_image.update(delta)

        self.text_helper.update()

        self.fade.update()
        self.splash_fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.tilemap.render_map(main_surface)

        self.layered_sprites.draw(main_surface)

        main_surface.blit(self.assets.start_labels[2], Vector2(TS*6, TS*13))
        main_surface.blit(self.assets.start_labels[3], Vector2(TS*3, TS*14))
        main_surface.blit(self.assets.start_labels[4], Vector2(TS*3, TS*15))
        main_surface.blit(self.assets.start_labels[5], Vector2(TS*2, TS*16))

        self.text_helper.render(main_surface)

        self.fade_surface.set_alpha(self.fade.alpha)
        self.splash_fade_surface.set_alpha(self.splash_fade.alpha)

        main_surface.blit(self.splash_fade_surface, Vector2(0, 0))
        self.splash_image.render(main_surface)
        main_surface.blit(self.fade_surface, Vector2(0, 0))


        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))


class Titles(Scene):

    def __init__(self, director):
        self.director = director
        self.assets = director.assets
        self.scene_name = 'Titles'

        self.fade = objects.SceneFadeInOut(FADEINOUT_DURATION)
        self.fade_surface = pygame.Surface((WIN_W, WIN_H)).convert()

        self.key_control = objects.KeyControl()

        self.all_objects = pygame.sprite.Group()
        self.layered_sprites = pygame.sprite.LayeredUpdates()

        self.titles_pos = Vector2(0, TS*3)
        self.titles_shift = Vector2(0, 0)
        self.render_window = Vector2(15, 10) # tiles

        self.cond_group = None


    def on_transitionto(self, transitionto_args):
        if DEBUG: print('{} on_transitionto'.format(self.scene_name))

        self.director.cut_scene = False

        self.fade_surface.fill(pygame.Color('black'))
        self.fade.fade_in()


    def handle_events(self, events):
        for event in events:
            # Exit game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.director.quit()

            # Handle player input
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if not self.director.cut_scene:
                    self.key_control.handle_key_events(event)


    def update(self, delta):
        self.all_objects.update(delta)

        if self.key_control.z:
            self.director.quit()
            self.key_control.clear_keys()
            return

        if self.key_control.up:
            if self.titles_shift.y > 0:
                if DEBUG: print('TODOLIST ^')
                self.titles_shift.y -= 1
                self.assets.sounds['scroll'].play()
                self.key_control.clear_keys()

        if self.key_control.down:
            if self.titles_shift.y < (self.assets.titles_surf.get_height()//TS)-self.render_window.y:
                if DEBUG: print('TODOLIST  V')
                self.titles_shift.y += 1
                self.assets.sounds['scroll'].play()
                self.key_control.clear_keys()

        self.fade.update()


    def render(self, screen):
        main_surface = pygame.Surface((WIN_W, WIN_H)).convert()
        main_surface.fill(pygame.Color('black'))

        # Render objects here
        self.layered_sprites.draw(main_surface)

        self.fade_surface.set_alpha(self.fade.alpha)

        main_surface.blit(self.assets.start_labels[0], Vector2(0, TS))
        main_surface.blit(self.assets.ip_selected_imgs['lens'], Vector2(TS*6, TS))
        main_surface.blit(self.assets.start_labels[1], Vector2(TS*7, TS))

        # Рендер картинки в рект
        if (self.assets.titles_surf.get_height()//TS) > self.render_window.y:
            subsurface = self.assets.titles_surf.subsurface(pygame.Rect(0, TS*self.titles_shift.y, TS*self.render_window.x, TS*self.render_window.y))
        else:
            subsurface = self.assets.titles_surf.subsurface(pygame.Rect(0, TS*self.titles_shift.y, TS*self.render_window.x, TS*(self.assets.titles_surf.get_height()//TS)))

        main_surface.blit(subsurface, self.titles_pos)

        if (self.assets.titles_surf.get_height()//TS) > self.render_window.y:
            if self.titles_shift.y > 0:
                main_surface.blit(self.assets.labels['up'], (TS*15, TS*2))
            if self.titles_shift.y < (self.assets.titles_surf.get_height()//TS)-self.render_window.y:
                main_surface.blit(self.assets.labels['down'], (TS*15, TS*14))

        # PICO8 symbols подсказки кнопок
        locs = {'quit':Vector2(TS*2, TS*16)}
        for item in locs.items():
            main_surface.blit(self.assets.labels[item[0]], item[1])

        main_surface.blit(self.fade_surface, Vector2(0, 0))

        screen.blit(pygame.transform.scale(main_surface, (settings.app.END_WIN_W, settings.app.END_WIN_H)), (0, 0))
