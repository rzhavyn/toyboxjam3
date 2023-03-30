import enum
import random
import copy
import math

import pygame
from pytmx import TiledTileLayer

import text_mono
import settings
import scenes

TS = settings.app.TS
DEBUG = settings.DEBUG
Vector2 = pygame.math.Vector2


class KeyControl(object):

    def __init__(self):
        self.key_map = {'L': pygame.K_LEFT, 'R': pygame.K_RIGHT, 'U': pygame.K_UP, 'D': pygame.K_DOWN,
                        'X': pygame.K_x, 'Z': pygame.K_z}

        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
        self.x = 0
        self.z = 0


    def handle_key_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.key_map['L']:
                self.left = 1
            elif event.key == self.key_map['R']:
                self.right = 1
            elif event.key == self.key_map['U']:
                self.up = 1
            elif event.key == self.key_map['D']:
                self.down = 1
            elif event.key == self.key_map['X']:
                self.x = 1
            elif event.key == self.key_map['Z']:
                self.z = 1

        elif event.type == pygame.KEYUP:
            if event.key == self.key_map['L']:
                self.left = 0
            elif event.key == self.key_map['R']:
                self.right = 0
            elif event.key == self.key_map['U']:
                self.up = 0
            elif event.key == self.key_map['D']:
                self.down = 0
            elif event.key == self.key_map['X']:
                self.x = 0
            elif event.key == self.key_map['Z']:
                self.z = 0


    def clear_keys(self):
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
        self.x = 0
        self.z = 0


class SceneFadeInOut(object):

    def __init__(self, duration):
        self.duration = duration
        self.time_elapsed = 0.0
        self.alpha = 255
        self.dir = None # 'in', 'out'
        self.finished_in = False
        self.finished_out = False


    def update(self):
        if self.dir == 'in' and not self.finished_in:
            self.time_elapsed += 1.0
            if self.time_elapsed >= self.duration:
                self.finished_in = True
            else:
                self.alpha = 256*(1.0-((4*self.time_elapsed)/float(self.duration)))

        elif self.dir == 'out' and not self.finished_out:
            self.time_elapsed += 1.0
            if self.time_elapsed >= self.duration:
                self.finished_out = True
            else:
                self.alpha = 256*((4*self.time_elapsed)/float(self.duration))


    def fade_in(self):
        self.dir = 'in'
        self.time_elapsed = 0.0
        self.finished_in = False
        self.finished_out = False


    def fade_out(self):
        self.dir = 'out'
        self.time_elapsed = 0.0
        self.finished_in = False
        self.finished_out = False


class TextHelper(object):

    def __init__(self, parent, text_helpers):
        self.parent = parent
        self.text_helpers = text_helpers

        self.render_text = False

        self.image = None
        self.rect = None

        self.shift_pos = Vector2(0, TS*8)
        self.shift_delay = 10
        self.shift_timer = 0
        self.add_delay = 15

        self.left_border = None
        self.dir = Vector2(-1, 0)
        self.shift_in_reverse = False


    def set_helper(self, room, object):
        self.render_text = True

        # BossBriefroom
        if object == 'talk_to_boss':
            self.image = self.text_helpers[room][0]

        # Corridor
        elif object == 'door_to_Archive':
            self.image = self.text_helpers[room][0]
        elif object == 'door_to_Jail':
            self.image = self.text_helpers[room][1]
        elif object == 'door_to_Office':
            self.image = self.text_helpers[room][2]
        elif object == 'check_time':
            self.image = self.text_helpers[room][3]
        elif object == 'talk_to_janitor':
            self.image = self.text_helpers[room][4]

        # Archive
        elif object == 'talk_to_archivist':
            self.image = self.text_helpers[room][0]
        elif object == 'use_archive_comp':
            self.image = self.text_helpers[room][1]

        # Jail
        elif object == 'door_to_Corridor':
            self.image = self.text_helpers[room][0]
        elif object == 'ladder_climb_up':
            self.image = self.text_helpers[room][1]
        elif object == 'ladder_go_down':
            self.image = self.text_helpers[room][2]
        elif object == 'talk_to_lawyer':
            self.image = self.text_helpers[room][3]
        elif object == 'talk_to_suspect':
            self.image = self.text_helpers[room][4]

        # Office
        elif object == 'talk_to_cop1':
            self.image = self.text_helpers[room][0]
        elif object == 'talk_to_cop2':
            self.image = self.text_helpers[room][1]
        elif object == 'use_player_comp':
            self.image = self.text_helpers[room][2]

        # Entrance
        elif object == 'talk_to_dutyofficer':
            self.image = self.text_helpers[room][0]
        elif object == 'talk_to_witness':
            self.image = self.text_helpers[room][1]

        # Start
        elif object == 'door_to_Entrance':
            self.image = self.text_helpers[room][0]
            self.shift_pos = Vector2(0, TS*12) # сдвиг text_helper вниз
        elif object == 'ladder_climb_up_start':
            self.image = self.text_helpers[room][1]
            self.shift_pos = Vector2(0, TS*12)
        elif object == 'ladder_go_down_start':
            self.image = self.text_helpers[room][2]
            self.shift_pos = Vector2(0, TS*12)

        self.rect = self.image.get_rect(topleft = self.shift_pos) # Vector2(0, TS*13)
        self.left_border = TS*16-self.image.get_width()


    def update(self):
        if self.render_text:
            if self.image.get_width() > TS*16:
                if self.shift_pos.x == 0:
                    self.shift_in_reverse = False
                    if self.shift_timer == 0:
                        self.shift_timer = self.shift_delay+self.add_delay

                if self.shift_pos.x > self.left_border and not self.shift_in_reverse:
                    self.dir = Vector2(-1, 0)
                    if self.shift_timer == 0:
                        self.shift_timer = self.shift_delay
                else:
                    self.dir = Vector2(1, 0)
                    if self.shift_timer == 0:
                        if self.shift_pos.x == self.left_border:
                            self.shift_timer = self.shift_delay+self.add_delay
                        else:
                            self.shift_timer = self.shift_delay
                        self.shift_in_reverse = True

                self.rect.topleft = Vector2(round(self.shift_pos.x), round(self.shift_pos.y))

                if self.shift_timer >= 0:
                    self.shift_timer -= 1
                    if self.shift_timer == 0:
                        self.shift_pos.x += TS*self.dir.x


    def clear_helper(self):
        self.render_text = False
        self.image = None
        self.rect = None
        self.shift_pos = Vector2(0, TS*8)
        self.shift_timer = 0
        self.left_border = None
        self.shift_in_reverse = False
        self.dir = Vector2(-1, 0)


    def render(self, surface):
        if self.render_text:
            surface.blit(self.image, self.rect)






class TileMap(object):

    def __init__(self, tmx_data, shift=Vector2(0, 0)):
        self.tmx_data = tmx_data

        self.tw = self.tmx_data.tilewidth
        self.th = self.tmx_data.tileheight

        self.shift = shift


    def render_tile_layer(self, surface, layer):
        for x, y, image in layer.tiles():
            surface.blit(image, ((x+self.shift.x)*self.tw, (y+self.shift.y)*self.th))


    def render_map(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                self.render_tile_layer(surface, layer)


class Passage(pygame.sprite.Sprite):

    def __init__(self, parent, pos, way_from, way_to, exit_dir):
        super().__init__()

        self.parent = parent

        self.way_from = way_from
        self.way_to = way_to
        self.exit_dir = exit_dir

        self.image = pygame.Surface((TS*2, TS*2)).convert()
        self.image.set_colorkey(pygame.Color('black'))
        self.image.fill(pygame.Color('black'))
        if DEBUG: pygame.draw.rect(self.image, pygame.Color('green'), pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()), 1)
        self.rect = self.image.get_rect(topleft = pos)

        self.active = False
        self.one_touch = False # для однократного прохода


    def update(self, delta):
        player = self.parent.player

        # Переход в другую комнату
        if self.parent.fade.finished_out:
            if self.active:
                player_pos = settings.player_locs[self.way_to]['from_'+self.way_from]

                args_dict = {'player_pos': player_pos,
                             'player_facing': player.facing}

                self.one_touch = False
                self.active = False

                player.kill()
                self.parent.player_indicator.kill()

                if self.parent.cond_group != None:
                    for c in self.parent.cond_group:
                        c.emit_start = False

                self.parent.director.go_to(self.way_to, args_dict)
                return

        # Задание точек перехода Игроку (однократное по коллизии Игрока с rect перехода)
        if self.rect.colliderect(player.rect) and not self.one_touch:
            self.one_touch = True
            # Активный переход!
            self.active = True

            if player.facing == '_l':
                to_player = (Vector2(player.rect.center)-Vector2(self.rect.left, self.rect.centery)).normalize()
                dot = Vector2(-1, 0).dot(to_player)

                if DEBUG: print('facing LEFT', dot)

                if dot < 0:
                    if DEBUG: print('dot < 0')
                    player.waypoints.append(Vector2(self.rect.right, self.rect.centery)) # start
                    # Включить фейдаут сцены (направление выхода налево)
                    if self.exit_dir == Vector2(-1, 0):
                        self.parent.fade.fade_out()
                        # удлиннить перемещение при переходе сцены
                        player.waypoints.append(Vector2(self.rect.left-TS*4, self.rect.centery)) # target
                    else:
                        player.waypoints.append(Vector2(self.rect.left-TS, self.rect.centery)) # target
                    if DEBUG: print('PLAYER GET WAYPOINTS:', player.waypoints)
                    player.state = ActorState.RUN

                    self.parent.director.cut_scene = True

                if dot > 0:
                    if DEBUG: print('\tdot > 0')

            else:
                to_player = (Vector2(self.rect.right, self.rect.centery)-Vector2(player.rect.center)).normalize()
                dot = Vector2(1, 0).dot(to_player)

                if DEBUG: print('facing RIGHT', dot)

                if dot > 0:
                    if DEBUG: print('dot > 0')
                    player.waypoints.append(Vector2(self.rect.left-TS, self.rect.centery))
                    # Включить фейдаут сцены (направление выхода направо)
                    if self.exit_dir == Vector2(1, 0):
                        self.parent.fade.fade_out()
                        # удлиннить перемещение при переходе сцены
                        player.waypoints.append(Vector2(self.rect.right+TS*3, self.rect.centery)) # target
                    else:
                        player.waypoints.append(Vector2(self.rect.right, self.rect.centery)) # target
                    if DEBUG: print('PLAYER GET WAYPOINTS:', player.waypoints)
                    player.state = ActorState.RUN

                    self.parent.director.cut_scene = True

                if dot < 0:
                    if DEBUG: print('\tdot < 0')

        # Сброс (при перемещении игрока с rect)
        if not self.rect.colliderect(player.rect) and self.one_touch:
            if DEBUG: print('PLAYER GET OFF RECT')

            if player.facing == '_l':
                # Направление выхода и facing игрока разнонаправлены (игрок просто сходит с перехода во время перехода из другой комнаты)
                if self.exit_dir != Vector2(-1, 0):
                    self.one_touch = False
                    self.active = False

            if player.facing == '_r':
                if self.exit_dir != Vector2(1, 0):
                    self.one_touch = False
                    self.active = False



class Door(pygame.sprite.Sprite):

    def __init__(self, parent, pos, way_from, way_to):
        super().__init__()

        self.parent = parent

        self.way_from = way_from
        self.way_to = way_to

        self.closed_img = pygame.Surface((TS*2, TS*2)).convert()
        self.closed_img.set_colorkey(pygame.Color('black'))
        self.closed_img.fill(pygame.Color('black'))
        if DEBUG: pygame.draw.rect(self.closed_img, pygame.Color('yellow'), pygame.Rect(0, 0, TS*2, TS*2), 1)

        self.black_img = pygame.Surface((TS*2, TS*2)).convert()
        self.black_img.fill(pygame.Color('black'))
        if DEBUG: pygame.draw.rect(self.black_img, pygame.Color('yellow'), pygame.Rect(0, 0, TS*2, TS*2), 1)

        self.image = self.closed_img
        self.rect = self.image.get_rect(topleft = pos)

        self.active = False
        self.one_touch = False # для однократного открытия
        self.is_opened = False

        self.door_closing_delay = 4
        self.door_closing_timer = 0


    def update(self, delta):
        player = self.parent.player

        # Переход в другую комнату
        if self.parent.fade.finished_out:
            if self.active:
                player_pos = settings.player_locs[self.way_to]['from_'+self.way_from]

                player_facing = '_r'
                # При переходе со Start в игру
                close_door = False
                thought = None
                start_scene = False
                if self.way_to == 'Entrance' and self.way_from == 'Start':
                    player_facing = '_l'
                    close_door = True
                    thought = 'start1'
                    start_scene = True

                args_dict = {'player_pos': player_pos,
                             'player_facing': player_facing,# во всех случаях, кроме перехода со Start в игру
                             'close_door': close_door,
                             'thought': thought,
                             'start_scene': start_scene}

                player.kill()
                self.parent.player_indicator.kill()

                if self.parent.cond_group != None:
                    for c in self.parent.cond_group:
                        c.emit_start = False

                if self.way_from == 'Jail':
                    if self.parent.director.suspects_total != 0:
                        if self.parent.director.suspects_interr == self.parent.director.suspects_total:
                            if self.parent.director.ikit_try == settings.IKIT_ZERO:
                                if self.parent.director.true_criminal_finded:
                                    self.parent.director.questions['Corridor'][0] = False
                                    self.parent.director.questions['Corridor'][2] = False
                                else:
                                    self.parent.director.questions['Corridor'][0] = True
                                    self.parent.director.questions['Corridor'][2] = True
                                self.parent.director.questions['Corridor'][1] = False
                                self.parent.director.questions['Archive'] = True
                                self.parent.director.questions['Office'] = True
                                self.parent.director.questions['Entrance'] = False

                            if self.parent.director.ikit_made != settings.IKIT_ZERO:
                                self.parent.director.questions['Corridor'][0] = False
                                self.parent.director.questions['Corridor'][1] = False
                                self.parent.director.questions['Corridor'][2] = False
                                self.parent.director.questions['Archive'] = False
                                self.parent.director.questions['Office'] = False
                                self.parent.director.questions['Entrance'] = True

                self.one_touch = False
                self.parent.text_helper.clear_helper()

                self.parent.director.go_to(self.way_to, args_dict)
                return

        # Центр игрока находится в пределах rect Двери
        if player.rect.centerx > self.rect.left and player.rect.centerx < self.rect.right:
            if player.rect.centery > self.rect.top and player.rect.centery < self.rect.bottom:
                if self.parent.director.player_go_door:
                    if not self.is_opened:
                        self.is_opened = True

                # Однократно
                if not self.one_touch:
                    self.one_touch = True
                    # Показать текст подсказки
                    object = 'door_to_'+self.way_to
                    self.parent.text_helper.set_helper(self.way_from, object)

                    # при открытой двери
                    if self.is_opened:
                        player.facing = '_r' # всегда!
                        player.waypoints.append(Vector2(self.rect.right-TS, self.rect.centery)) # start
                        player.waypoints.append(Vector2(self.rect.right, self.rect.centery)) # target
                        player.state = ActorState.RUN

                        self.parent.director.cut_scene = True

                        self.active = False


                # Игрок нажал X, находясь в коллизии с rect двери
                if player.key_control.x:
                    if not self.parent.director.start_scene:
                        self.is_opened = True
                        self.active = True
                        # Включить фейдаут сцены
                        self.parent.fade.fade_out()

                        self.parent.director.player_go_door = True
                        self.parent.director.cut_scene = True
                        player.key_control.clear_keys()
                    else:
                        if self.parent.director.true_criminal_finded:
                            self.parent.director.current_thought = 'win2'
                        else:
                            self.parent.director.current_thought = 'start3'
                        self.parent.dialogue_box.show_thoughts(self.parent.director.current_thought)

        else:
            # Сброс одноразового столкновения (при перемещении игрока с/по rect)
            if self.one_touch:
                self.one_touch = False
                self.parent.text_helper.clear_helper()

                if self.is_opened:
                    # Закрыть дверь (изображение) с задержкой
                    self.door_closing_timer = self.door_closing_delay
                return

        # Таймер закрытия двери
        if self.door_closing_timer >= 0:
            self.door_closing_timer -= 1

            if self.door_closing_timer == 0:
                self.is_opened = False
                self.parent.director.player_go_door = False
                self.parent.assets.sounds['door'].play()

        # Обновить изображение
        if self.is_opened:
            self.image = self.black_img
        else:
            self.image = self.closed_img



class Ladder(pygame.sprite.Sprite):

    def __init__(self, parent, pos):
        super().__init__()

        self.parent = parent

        self.image = pygame.Surface((TS, TS*4)).convert()
        self.image.set_colorkey(pygame.Color('black'))
        self.image.fill(pygame.Color('black'))
        if DEBUG: pygame.draw.rect(self.image, pygame.Color('dodgerblue'), pygame.Rect(0, 0, TS, TS*4), 1)
        self.rect = self.image.get_rect(topleft = pos)

        self.one_touch = False # для однократного перемещения
        self.player_moving_on_ladder = False

        self.high_point = Vector2(self.rect.topleft) # верх
        self.low_point = Vector2(self.rect.left, self.rect.bottom-TS) # подножие


    def update(self, delta):
        player = self.parent.player

        if player.rect.centerx > self.rect.left and player.rect.centerx < self.rect.right:
            if player.rect.centery > self.rect.top and player.rect.centery < self.rect.bottom:
                # Однократно
                if not self.one_touch:
                    self.one_touch = True
                    # Показать текст подсказки
                    if player.rect.centery > self.rect.centery:
                        object = 'ladder_climb_up'
                        if self.parent.scene_name == 'Start':
                            object = 'ladder_climb_up_start'
                    elif player.rect.centery < self.rect.centery:
                        object = 'ladder_go_down'
                        if self.parent.scene_name == 'Start':
                            object = 'ladder_go_down_start'

                    if self.parent.scene_name == 'Jail':
                        self.parent.text_helper.set_helper('Jail', object)
                    elif self.parent.scene_name == 'Start':
                        self.parent.text_helper.set_helper('Start', object)

                # Нажатие X
                if player.key_control.x:
                    if not self.player_moving_on_ladder:
                        self.parent.director.cut_scene = True
                        player.state = ActorState.CLIMB

                        # Находясь у подножия лестницы
                        if player.rect.centery > self.rect.centery:
                            if DEBUG: print('PLAYER WAYPOINTS SET CLIMB UP', player.rect.centery, self.rect.centery)
                            self.player_moving_on_ladder = True
                            player.waypoints.append(Vector2(player.rect.topleft))
                            player.waypoints.append(Vector2(self.rect.left, self.rect.bottom-TS)) # target подножие
                            player.waypoints.append(Vector2(self.rect.topleft)) # target верх
                            # player.waypoints.append(self.low_point)
                            # player.waypoints.append(self.high_point)
                            return

                        # Находясь наверху лестницы
                        if player.rect.centery < self.rect.centery:
                            if DEBUG: print('PLAYER WAYPOINTS SET GO DOWN', player.rect.centery, self.rect.centery)
                            self.player_moving_on_ladder = True
                            player.waypoints.append(Vector2(player.rect.topleft))
                            player.waypoints.append(Vector2(self.rect.topleft)) # target верх
                            player.waypoints.append(Vector2(self.rect.left, self.rect.bottom-TS)) # target подножие
                            # player.waypoints.append(self.high_point)
                            # player.waypoints.append(self.low_point)
                            return

        else:
            # Сброс одноразового столкновения (при перемещении игрока с rect)
            if self.one_touch:
                self.player_moving_on_ladder = False

                self.one_touch = False
                self.parent.text_helper.clear_helper()






class ActorState(enum.Enum):

    IDLE = 'idle'
    RUN = 'run'
    CLIMB = 'climb'
    TALK = 'talk'


class Actor(pygame.sprite.Sprite):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.animation_set = None
        self.animation_frame = 0
        self.imgs_per_frame = 0
        self.current_animation = None


    def set_animation_set(self, animation_set):
        self.animation_set = animation_set.copy()
        self.animation_frame = 0
        self.imgs_per_frame = 0


    def next_animation_frame(self, anim_set_key):
        self.imgs_per_frame += 1

        if self.animation_set != None:
            # Сброс при смене анимации
            if self.current_animation != anim_set_key:
                self.current_animation = anim_set_key
                self.animation_frame = 0
                self.imgs_per_frame = 0

            anim_set_seq = self.animation_set['anim_seq'][anim_set_key]
            anim_set_frames = self.animation_set['anim_frames'][anim_set_key]

            # Переключить на следующий кадр анимации
            if self.imgs_per_frame >= anim_set_seq[self.animation_frame][1]:
                self.animation_frame += 1
                self.imgs_per_frame = 0

            # Зациклить анимацию
            if self.animation_frame >= len(anim_set_frames):
                self.animation_frame = 0
                self.imgs_per_frame = 0




class Coin(Actor):

    def __init__(self, parent, pos):
        self._layer = 3

        super().__init__(parent)

        self.set_animation_set(self.parent.assets.coin_anim_set)

        anim_set_frames = self.animation_set['anim_frames']['idle']
        self.image = anim_set_frames[0]
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.state = ActorState.IDLE

        self.vel = Vector2(0, 0)
        self.vertical_momentum = 0.4
        self.GRAVITY = 0.5
        self.MAX_FALL_SPEED = 6


    def update(self, delta):
        if self.rect.top > TS*8:
            self.kill()

        self.vel.y += self.vertical_momentum
        if self.vel.y > self.MAX_FALL_SPEED:
            self.vel.y = self.MAX_FALL_SPEED

        self.vertical_momentum += self.GRAVITY

        self.pos.y += self.vel.y
        self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

        # Апдейт картинки согласно текущей анимации и ее кадру
        anim_set_key = self.state.value
        self.next_animation_frame(anim_set_key)
        anim_set_frames = self.animation_set['anim_frames'][anim_set_key]
        self.image = anim_set_frames[self.animation_frame]



class Player(Actor):

    def __init__(self, parent, pos, facing, animation_set):
        self._layer = 3

        super().__init__(parent)

        self.director = parent.director

        self.set_animation_set(animation_set)

        self.facing = facing
        self.state = ActorState.IDLE

        anim_set_frames = self.animation_set['anim_frames'][self.state.value+self.facing]
        self.image = anim_set_frames[0]
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.key_control = KeyControl()

        self.speed = 2
        self.map_bbox = self.parent.map_bounding_box

        self.waypoints = []
        self.target_waypoint = None
        self.target_idx = 1
        self.moving_waypoints = False


    def update(self, delta):
        if self.waypoints == []:
            if not self.parent.director.cut_scene:
                # Обработка ввода Игрока
                if self.key_control.left:
                    if DEBUG: print('PRESSED LEFT <')
                    self.pos.x -= self.speed
                    self.facing = '_l'
                    self.state = ActorState.RUN

                elif self.key_control.right:
                    if DEBUG: print('PRESSED RIGHT >')
                    self.pos.x += self.speed
                    self.facing = '_r'
                    self.state = ActorState.RUN

                else:
                    self.state = ActorState.IDLE

                # Ограничить перемещения игрока
                if self.pos.x < self.map_bbox.left:
                    self.pos.x = self.map_bbox.left
                if self.pos.x > self.map_bbox.right:
                    self.pos.x = self.map_bbox.right

        else:
            if DEBUG: print('PLAYER GO WAYPOINTS:', self.pos, 'to', self.target_waypoint, self.moving_waypoints, self.waypoints)
            # Перемещение по заданным точкам пути
            if self.target_waypoint == None:
                self.target_waypoint = self.waypoints[self.target_idx]
                self.pos = self.waypoints[0]
                self.moving_waypoints = True

                self.key_control.clear_keys()

            if self.moving_waypoints:
                distance_to = self.pos.distance_to(self.target_waypoint)

                if distance_to > self.speed:
                    self.pos = self.pos + (self.target_waypoint - self.pos).normalize() * self.speed
                    # self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

                else:
                    if DEBUG: print('D<S')
                    self.pos = self.target_waypoint
                    # self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

                    self.target_idx += 1

                    if self.target_idx < len(self.waypoints):
                        # найти следующую точку
                        self.target_waypoint = self.waypoints[self.target_idx]
                    else:
                        # Прекратить движение
                        self.waypoints = []
                        self.target_waypoint = None
                        self.target_idx = 1
                        self.moving_waypoints = False

                        self.director.cut_scene = False
                        self.state = ActorState.IDLE
                        if DEBUG: print('TRANSITION FINISHED')

        self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

        # if self.key_control.x:
        #     print('PRESSED X')
        #
        # if self.key_control.z:
        #     print('PRESSED Z (PICO-8 O)')

        # Апдейт картинки согласно текущей анимации и ее кадру
        # Анимация Climb не имеет направления лево-право
        if self.state != ActorState.CLIMB:
            anim_set_key = self.state.value+self.facing
        else:
            anim_set_key = self.state.value
        self.next_animation_frame(anim_set_key)
        anim_set_frames = self.animation_set['anim_frames'][anim_set_key]
        self.image = anim_set_frames[self.animation_frame]



class NPC(Actor):

    def __init__(self, parent, pos, npc_type, npc_scene_name, talk_rect, ikit_parts=None, wander_point=None, jail_cell=None, wander_delay=0):
        self._layer = 2

        super().__init__(parent)

        self.director = parent.director
        self.scene_name = parent.scene_name
        self.npc_scene_name = npc_scene_name
        self.ikit_parts = ikit_parts
        self.jail_cell = jail_cell

        self.npc_type = npc_type
        self.set_animation_set(self.director.assets.npc_anim_sets[npc_type])

        self.state = ActorState.IDLE

        anim_set_frames = self.animation_set['anim_frames'][self.state.value]
        self.image = anim_set_frames[0]
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.talk_rect = talk_rect
        self.show_texthelper = False

        self.speed = 2

        if wander_point:
            self.waypoints = [pos, wander_point]
        else:
            self.waypoints = []
        self.current_waypoint = None
        self.target_waypoint = None
        self.target_idx = 1
        self.moving_waypoints = False

        self.wander_step_delay = wander_delay
        self.wander_step_timer = 0

        self.dialog_opens_new_scene = False
        self.opens_scene = None
        self.active = False

        self.refuse_to_talk = False

        self.start_scene_auto_done = False


    def update(self, delta):
        player = self.parent.player

        if self.dialog_opens_new_scene:
            if self.active:
                if self.parent.fade.finished_out:
                    args_dict = {'player_pos': Vector2(player.rect.topleft),
                                 'player_facing': player.facing,
                                 'criminal_parts':self.ikit_parts}

                    player.kill()
                    self.parent.player_indicator.kill()

                    self.active = False

                    self.director.go_to(self.opens_scene, args_dict)
                    return

        if player.rect.centerx > self.talk_rect.left and player.rect.centerx < self.talk_rect.right:
            if player.rect.centery > self.talk_rect.top and player.rect.centery < self.talk_rect.bottom:
                # Однократно
                if not self.show_texthelper:
                    self.show_texthelper = True
                    # Показать текст подсказки
                    object = 'talk_to_'+self.npc_scene_name # у подозреваемого suspect
                    self.parent.text_helper.set_helper(self.scene_name, object)
                    if DEBUG: print('TALK')

                # Стартовая сцена игры, авто разговор DO с игроком
                if self.npc_scene_name == 'dutyofficer':
                    if not self.start_scene_auto_done:
                        if self.director.start_scene:
                            self.start_scene_auto_done = True

                            self.parent.top_black.show = True
                            self.parent.bottom_black.show = True

                            self.parent.dialogue_box.show_talks(self, 'start_scene')
                            self.director.cut_scene = True

                            self.state = ActorState.TALK
                            player.state = ActorState.IDLE

                            player.key_control.clear_keys()
                            self.parent.key_control.clear_keys()

                # Нажатие X
                if player.key_control.x:
                    if DEBUG: print('START CONVERSATION')

                    self.parent.top_black.show = True
                    self.parent.bottom_black.show = True

                    if self.npc_scene_name == 'boss':
                        if not self.director.case_given:
                            if self.director.true_criminal_finded:
                                # DEMO END
                                self.parent.dialogue_box.show_talks(self, 'win')
                            else:
                                # Новое дело
                                self.parent.dialogue_box.show_talks(self, 'new_clues')
                        else:
                            self.parent.dialogue_box.show_talks(self, 'chat')

                    elif self.npc_scene_name == 'witness':
                        if self.refuse_to_talk:
                            self.parent.dialogue_box.show_talks(self, 'chat')
                        else:
                            self.parent.dialogue_box.show_talks(self, 'add_clue')

                    elif self.npc_scene_name == 'dutyofficer':
                        if self.director.start_scene:
                            if DEBUG: print('NPC-DO-start scene-start scene')
                            self.parent.dialogue_box.show_talks(self, 'start_scene')
                        else:
                            if self.director.case_given:
                                if self.director.ikit_made != settings.IKIT_ZERO:
                                    if DEBUG: print('NPC-DO-case given-send target')
                                    self.parent.dialogue_box.show_talks(self, 'send_target')
                                else:
                                    if self.director.ikit_try != settings.IKIT_ZERO:
                                        if DEBUG: print('NPC-DO-case given-not finalized')
                                        self.parent.dialogue_box.show_talks(self, 'not_finalized')
                                    else:
                                        self.parent.dialogue_box.show_talks(self, 'chat')
                            else:
                                self.parent.dialogue_box.show_talks(self, 'chat')

                    elif self.npc_scene_name == 'suspect':
                        if self.refuse_to_talk:
                            self.parent.dialogue_box.show_talks(self, 'chat')
                        else:
                            if DEBUG: print('\twith SUSPECT')
                            self.dialog_opens_new_scene = True
                            self.opens_scene = 'Interrogation'

                            self.refuse_to_talk = True

                            if self.jail_cell == 'L_U':
                                self.director.questions['Jail'][0] = False
                            if self.jail_cell == 'R_U':
                                self.director.questions['Jail'][1] = False
                            if self.jail_cell == 'L_D':
                                self.director.questions['Jail'][2] = False
                            if self.jail_cell == 'R_D':
                                self.director.questions['Jail'][3] = False

                            self.director.suspects_interr += 1

                            self.active = True

                            self.parent.text_helper.clear_helper()

                            # Включить фейдаут сцены
                            self.parent.fade.fade_out()
                            self.director.cut_scene = True
                            player.key_control.clear_keys()

                    else:
                        self.parent.dialogue_box.show_talks(self, 'chat')

                    self.director.cut_scene = True

                    self.state = ActorState.TALK
                    player.state = ActorState.IDLE

                    player.key_control.clear_keys()
                    self.parent.key_control.clear_keys()

        else:
            # Сброс (при перемещении игрока с rect)
            if self.show_texthelper:
                self.show_texthelper = False
                self.parent.text_helper.clear_helper()

        if self.waypoints != []:
            if not self.target_waypoint:
                self.target_waypoint = self.waypoints[self.target_idx]
                self.pos = self.waypoints[0]
                self.moving_waypoints = True
                self.state = ActorState.RUN

            if self.moving_waypoints:
                distance_to = self.pos.distance_to(self.target_waypoint)

                if distance_to > self.speed:
                    self.pos = self.pos + (self.target_waypoint - self.pos).normalize() * self.speed
                else:
                    self.pos = self.target_waypoint

                    self.target_idx += 1

                    if self.target_idx < len(self.waypoints):
                        self.target_waypoint = self.waypoints[self.target_idx]
                    else:
                        self.wander_step_timer = self.wander_step_delay
                        self.moving_waypoints = False
                        self.state = ActorState.IDLE

        self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

        # Таймер задержки шагов брожения
        if self.wander_step_timer >= 0:
            self.wander_step_timer -= 1

            if self.wander_step_timer == 0:
                # Зациклить перемещение
                self.target_idx = 1
                self.target_waypoint = None
                self.moving_waypoints = True
                self.waypoints.reverse()

        # Апдейт картинки согласно текущей анимации и ее кадру
        anim_set_key = self.state.value
        self.next_animation_frame(anim_set_key)
        anim_set_frames = self.animation_set['anim_frames'][anim_set_key]
        self.image = anim_set_frames[self.animation_frame]






class Indicator(pygame.sprite.Sprite):

    def __init__(self, parent):
        self._layer = 3

        super().__init__()

        self.parent = parent
        self.assets = parent.director.assets
        self.player = parent.player
        self.item_type = None

        self.transp_image = pygame.Surface((TS, TS)).convert()
        self.transp_image.set_colorkey(pygame.Color('black'))
        self.transp_image.fill(pygame.Color('black'))

        self.image = self.transp_image
        self.pos = Vector2(self.player.rect.x, self.player.rect.y-TS)
        self.rect = self.image.get_rect(topleft = self.pos)


    def set_item_type(self, item_type):
        self.item_type = item_type


    def update(self, delta):
        if self.item_type == 'try_ikit':
            self.image = self.assets.indicator_imgs['try_ikit']
        elif self.item_type == 'made_ikit':
            self.image = self.assets.indicator_imgs['made_ikit']
        else:
            self.image = self.transp_image

        self.pos = Vector2(self.player.rect.x, self.player.rect.y-TS)
        self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))






class InteractionObject(pygame.sprite.Sprite):

    def __init__(self, parent, pos, img_size, interact_rect, object_name, scene_name, opens_new_scene, way_to):
        super().__init__()

        self.parent = parent

        self.image = pygame.Surface((img_size[0], img_size[1])).convert()
        self.image.set_colorkey(pygame.Color('black'))
        self.image.fill(pygame.Color('black'))
        if DEBUG: pygame.draw.rect(self.image, pygame.Color('palevioletred'), pygame.Rect(0, 0, img_size[0], img_size[1]), 1)
        self.rect = self.image.get_rect(topleft = pos)

        self.interact_rect = interact_rect
        self.object_name = object_name
        self.scene_name = scene_name
        self.way_to = way_to
        self.opens_new_scene = opens_new_scene

        self.active = False
        self.show_texthelper = False


    def update(self, delta):
        player = self.parent.player

        # Переход в другую комнату
        if self.opens_new_scene:
            if self.parent.fade.finished_out:
                if self.active:
                    args_dict = {'player_pos': Vector2(player.rect.topleft),
                                 'player_facing': player.facing}

                    player.kill()
                    self.parent.player_indicator.kill()

                    self.active = False

                    self.parent.director.go_to(self.way_to, args_dict)
                    return

        if player.rect.centerx > self.interact_rect.left and player.rect.centerx < self.interact_rect.right:
            if player.rect.centery > self.interact_rect.top and player.rect.centery < self.interact_rect.bottom:
                # Однократно
                if not self.show_texthelper:
                    self.show_texthelper = True
                    # Показать текст подсказки
                    object = 'use_'+self.object_name
                    self.parent.text_helper.set_helper(self.scene_name, object)

                # Нажатие X
                if player.key_control.x:
                    if self.opens_new_scene:
                        if DEBUG: print('INTERACT WITH OBJECT-open new scene')
                        self.active = True

                        self.parent.text_helper.clear_helper()

                        # Включить фейдаут сцены
                        self.parent.fade.fade_out()
                        self.parent.director.cut_scene = True
                        player.key_control.clear_keys()
                    else:
                        if DEBUG: print('INTERACT WITH OBJECT-show dialog')

        else:
            # Сброс (при перемещении игрока с rect)
            if self.show_texthelper:
                self.show_texthelper = False
                self.parent.text_helper.clear_helper()








# case = {'ikit_part': 'upper', 'ikit_part_num': 3, 'case': str, 'assigned_hint': ['hint1','hint2','hint3']}

class Identikit(object):

    def __init__(self, parent, parts_locs, is_changeble=True, preview_kit=True):
        self.parent = parent
        self.assets = parent.assets
        self.key_control = parent.key_control

        self.cases = []
        if DEBUG: print('__init__ IKIT CASES:', self.cases)
        self.case_idx = 0

        self.parts_locs = parts_locs
        self.parts = pygame.sprite.Group()

        self.upper_part = IdentikitPart(self, parts_locs[0], 'upper')
        self.parts.add(self.upper_part)
        self.lower_part = IdentikitPart(self, parts_locs[1], 'lower')
        self.parts.add(self.lower_part)
        self.hair_part = IdentikitPart(self, parts_locs[2], 'hair')
        self.parts.add(self.hair_part)
        self.facial_hair_part = IdentikitPart(self, parts_locs[3], 'facial_hair')
        self.parts.add(self.facial_hair_part)

        self.parent.layered_sprites.add(self.upper_part)
        self.parent.layered_sprites.add(self.lower_part)
        self.parent.layered_sprites.add(self.hair_part)
        self.parent.layered_sprites.add(self.facial_hair_part)

        self.is_changeble = is_changeble
        self.once = False # однократное нажатие

        self.preview_kit = preview_kit


    def set_cases(self, cases):
        self.cases = cases


    def set_ikit_part(self, ikit_part, ikit_part_num):
        if ikit_part == 'upper':
            self.upper_part.change(ikit_part_num)
        elif ikit_part == 'lower':
            self.lower_part.change(ikit_part_num)
        elif ikit_part == 'hair':
            self.hair_part.change(ikit_part_num)
        elif ikit_part == 'facial_hair':
            self.facial_hair_part.change(ikit_part_num)


    def clean_parts(self):
        self.upper_part.change(0)
        self.lower_part.change(0)
        self.hair_part.change(0)
        self.facial_hair_part.change(0)
        self.case_idx = 0


    def get_parts_numbers(self):
        out = {'upper':self.upper_part.ikit_part_num, 'lower':self.lower_part.ikit_part_num,
               'hair':self.hair_part.ikit_part_num, 'facial_hair':self.facial_hair_part.ikit_part_num}
        return out


    def change_parts(self):
        if DEBUG: print('update IKIT CASES:', self.cases)
        cur_case = self.cases[self.case_idx]
        if DEBUG: print('Identikit-cur_case:', cur_case, self.case_idx)
        if DEBUG: print('Identikit-CHANGE CASE to', self.case_idx)

        if cur_case['ikit_part'] == 'upper':
            self.upper_part.change(cur_case['ikit_part_num'])
            self.lower_part.change(0)
            self.hair_part.change(0)
            self.facial_hair_part.change(0)
        elif cur_case['ikit_part'] == 'lower':
            self.upper_part.change(0)
            self.lower_part.change(cur_case['ikit_part_num'])
            self.hair_part.change(0)
            self.facial_hair_part.change(0)
        elif cur_case['ikit_part'] == 'hair':
            self.upper_part.change(0)
            self.lower_part.change(0)
            self.hair_part.change(cur_case['ikit_part_num'])
            self.facial_hair_part.change(0)
        elif cur_case['ikit_part'] == 'facial_hair':
            self.upper_part.change(0)
            self.lower_part.change(0)
            self.hair_part.change(0)
            self.facial_hair_part.change(cur_case['ikit_part_num'])

        self.once = False


    def update(self):
        if self.is_changeble:
            if self.key_control.left:
                if not self.once:
                    if DEBUG: print('IKIT <')
                    self.once = True
                    self.key_control.clear_keys()

                    self.case_idx -= 1
                    if self.case_idx < 0:
                        self.case_idx = len(self.cases)-1

                    self.change_parts()

            if self.key_control.right:
                if not self.once:
                    if DEBUG: print('IKIT >')
                    self.once = True
                    self.key_control.clear_keys()

                    self.case_idx += 1
                    if self.case_idx > len(self.cases)-1:
                        self.case_idx = 0

                    self.change_parts()

        self.parts.update()



class IdentikitPart(pygame.sprite.Sprite):

    def __init__(self, parent, pos, ikit_part):
        self._layer = 0

        super().__init__()

        self.parent = parent
        self.assets = parent.assets

        self.ikit_part = ikit_part # 'upper', 'lower', 'hair', 'facial_hair'
        self.ikit_part_num = 0 # ! 0 элемент всегда прозрачная пустая картинка

        self.image = self.assets.identikit_parts[self.ikit_part][self.ikit_part_num]
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.bald_part = False


    def change(self, ikit_part_num):
        self.ikit_part_num = ikit_part_num

        if not self.parent.preview_kit:
            if self.ikit_part == 'hair':
                if ikit_part_num == self.assets.bald_parts['hair'][0]:
                    self.bald_part = True
                else:
                    self.bald_part = False

            elif self.ikit_part == 'facial_hair':
                if ikit_part_num == self.assets.bald_parts['facial_hair'][0]:
                    self.bald_part = True
                else:
                    self.bald_part = False

        else:
            self.bald_part = False

    def update(self):
        if self.bald_part:
            self.image = self.assets.bald_parts[self.ikit_part][1]
        else:
            self.image = self.assets.identikit_parts[self.ikit_part][self.ikit_part_num]









class UIArrow(pygame.sprite.Sprite):

    def __init__(self, parent, pos, arrow_image_keys): # [norm_img, opposite_img]
        self._layer = 99

        super().__init__()

        self.arrow_image_keys = arrow_image_keys

        self.norm_image = parent.assets.active_arrows[self.arrow_image_keys[0]].copy()
        self.opposite_image = parent.assets.active_arrows[self.arrow_image_keys[1]].copy()

        self.no_image = self.norm_image.copy()
        self.no_image.set_colorkey(pygame.Color('magenta'))
        self.no_image.fill(pygame.Color('magenta'))

        self.image = self.norm_image
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.show = False
        self.show_opposite = False


    def set_pos(self, pos):
        self.pos = pos


    def update(self, delta):
        if self.show:
            if self.show_opposite:
                self.image = self.opposite_image
            else:
                self.image = self.norm_image
        else:
            self.image = self.no_image

        self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))


class UIHint(object):

    def __init__(self, parent, pos):
        self.parent = parent
        self.assets = parent.assets
        self.pos = pos

        self.hints_images = []
        self.def_image = pygame.Surface((TS*3, TS)).convert()

        self.archive_case_n = 0


    def set_hint(self, hints_list): #[['s', 's', 's'], [], ....]
        if DEBUG: print('SET hint:', hints_list)
        self.hints_images = []

        for i in range(len(hints_list)):
            if hints_list[i] != []:
                for j in range(len(hints_list[i])):
                    self.def_image.blit(self.assets.clues_icons[hints_list[i][j]], (TS*j, 0))
            else:
                self.def_image.fill(pygame.Color('black'))

            self.hints_images.append(self.def_image.copy())


    def update(self):
        if self.parent.identikit.case_idx != self.archive_case_n:
            self.set_hint([self.parent.identikit.cases[self.parent.identikit.case_idx]['assigned_hint']])
            self.archive_case_n = self.parent.identikit.case_idx


    def render(self, surface):
        for i, img in enumerate(self.hints_images):
            surface.blit(img, (self.pos.x, self.pos.y+TS*i))



class UIChangeFallIco(pygame.sprite.Sprite):

    def __init__(self, parent, pos, img):
        self._layer = 5

        super().__init__()

        self.image = img
        self.pos = pos
        self.rect = self.image.get_rect(topleft = pos)

        self.center_y = pos.y
        self.y_cff = 10
        self.init_pos = pos


    def update(self, delta):
        if self.rect.top >= self.init_pos.y+TS/2:
            self.kill()

        self.center_y += (TS*16-self.center_y)/self.y_cff
        self.rect.topleft = Vector2(round(self.pos.x), self.center_y)



class UISelect(pygame.sprite.Sprite):

    def __init__(self, parent, pos):
        self._layer = 4

        super().__init__()

        self.parent = parent

        self.lens_img = parent.assets.ip_selected_imgs['lens']
        self.lock_img = parent.assets.ip_selected_imgs['locked']

        self.no_image = pygame.Surface((TS, TS))
        self.no_image.set_colorkey(pygame.Color('magenta'))
        self.no_image.fill(pygame.Color('magenta'))

        self.locked = False
        self.show = False
        self.switch = False

        self.image = self.no_image
        self.pos = pos
        self.rect = self.no_image.get_rect(topleft = pos)


    def update(self, delta):
        if not self.locked:
            if self.show:
                self.image = self.lens_img
            else:
                self.image = self.no_image

            if self.switch:
                fallico = UIChangeFallIco(self, self.pos, self.lens_img)
                self.parent.all_objects.add(fallico)
                self.parent.layered_sprites.add(fallico)
                self.switch = False

        else:
            if self.show:
                self.image = self.lock_img
            else:
                self.image = self.no_image


class UIAnswer(pygame.sprite.Sprite):

    def __init__(self, parent, pos):
        self._layer = 99

        super().__init__()

        self.parent = parent

        self.no_image = pygame.Surface((TS, TS))
        self.no_image.set_colorkey(pygame.Color('magenta'))
        self.no_image.fill(pygame.Color('magenta'))

        self.image = self.no_image
        self.pos = pos
        self.rect = self.no_image.get_rect(topleft = pos)


    def set_answer(self, answer, hint=None):
        if answer == 'yes':
            phrase = 'YES({})'
            text_to_render = phrase.format(self.parent.assets.clue_to_text(hint[0]))
            self.image = text_mono.render_text(text_to_render, self.parent.assets.tile_font, 1)
        elif answer == 'no':
            text_to_render = 'NO!'
            self.image = text_mono.render_text(text_to_render, self.parent.assets.tile_font, 1)
        else:
            self.image = self.no_image









class DialogueBox(object):

    def __init__(self, parent, pos):
        self.director = parent.director
        self.parent = parent
        self.assets = parent.assets
        self.key_control = parent.key_control

        self.pos = pos
        self.shift = Vector2(0, 0)
        self.render_window = Vector2(14, 4) # tiles
        self.text_image = None
        self.label_image = None
        self.dash_image = text_mono.render_text('-', self.assets.tile_font, 1)

        self.conv_npc = None
        self.show_npc_talks = False
        self.show_player_thoughts = False


    def hide(self, to_hide):
        if to_hide == 'talks':
            self.show_npc_talks = False

        if to_hide == 'thoughts':
            self.show_player_thoughts = False


    def show_talks(self, talk_to_actor, talk_type):
        self.shift = Vector2(0, 0)
        self.show_player_thoughts = False
        self.conv_npc = talk_to_actor

        if self.conv_npc.npc_scene_name == 'boss':
            if talk_type == 'new_clues':
                # Каждое обращение к talk_type 'new_clues' удаляет одну из фраз из self.assets.boss_new_clues
                if len(self.assets.boss_new_clues) != 0:
                    phrase = self.assets.boss_new_clues.pop()
                    # Сгенерировать новое дело
                    self.director.generate_new_case()
                    text_to_render = phrase.format(self.assets.clue_to_text(self.director.investigated_clues[0]))
                labels = self.assets.talks['boss']['labels']
                label_to_render = random.choice(labels['new_clues'])
            elif talk_type == 'win':
                text_to_render = random.choice(self.assets.talks['boss']['win'])
                labels = self.assets.talks['boss']['labels']
                label_to_render = random.choice(labels['win'])
                self.director.game_ended = True
            elif talk_type == 'end':
                # DEMO END
                text_to_render = random.choice(self.assets.talks['boss']['end'])
                labels = self.assets.talks['boss']['labels']
                label_to_render = random.choice(labels['new_clues'])
            elif talk_type == 'chat':
                text_to_render = random.choice(self.assets.talks['boss']['chat'])
                labels = self.assets.talks['boss']['labels']
                label_to_render = random.choice(labels['chat'])
            name_to_render = 'BOSS:'

        elif self.conv_npc.npc_scene_name == 'dutyofficer':
            if talk_type =='start_scene':
                text_to_render = random.choice(self.assets.talks['dutyofficer']['start_scene'])
                labels = self.assets.talks['dutyofficer']['labels']
                label_to_render = random.choice(labels['chat'])
            elif talk_type == 'send_target':
                text_to_render = random.choice(self.assets.talks['dutyofficer']['send_target'])
                labels = self.assets.talks['dutyofficer']['labels']
                label_to_render = random.choice(labels['send_target'])
            elif talk_type == 'not_finalized':
                text_to_render = random.choice(self.assets.talks['dutyofficer']['not_finalized'])
                labels = self.assets.talks['dutyofficer']['labels']
                label_to_render = random.choice(labels['chat'])
            elif talk_type == 'chat':
                text_to_render = random.choice(self.assets.talks['dutyofficer']['chat'])
                labels = self.assets.talks['dutyofficer']['labels']
                label_to_render = random.choice(labels['chat'])
            name_to_render = self.assets.talks[self.conv_npc.npc_scene_name]['name']+':'

        elif self.conv_npc.npc_scene_name == 'witness':
            if talk_type == 'add_clue':
                phrase = self.assets.talks['witness']['add_clue'][0]
                a_hints = self.conv_npc.ikit_parts['assigned_hint']
                text_to_render = phrase.format(self.assets.clue_to_text(a_hints[0]), self.assets.clue_to_text(a_hints[1]),
                                               self.assets.clue_to_text(a_hints[2]))
                labels = self.assets.talks['witness']['labels']
                label_to_render = random.choice(labels['take'])
            elif talk_type == 'chat':
                text_to_render = random.choice(self.assets.talks['witness']['chat'])
                labels = self.assets.talks['witness']['labels']
                label_to_render = random.choice(labels['chat'])
            name_to_render = 'WITNESS:'

        else:
            npc_scene_name = self.conv_npc.npc_scene_name
            text_to_render = random.choice(self.assets.talks[npc_scene_name]['chat'])
            label_to_render = random.choice(self.assets.talks[npc_scene_name]['labels'])
            name_to_render = self.assets.talks[npc_scene_name]['name']+':'

        self.text_image = text_mono.render_text(text_to_render, self.assets.tile_font, 1, self.render_window.x)
        self.label_image = text_mono.render_text(label_to_render, self.assets.tile_font, 1)
        self.name_image = text_mono.render_text(name_to_render, self.assets.tile_font, 1, None, settings.pico_cyan)

        self.show_npc_talks = True


    def show_thoughts(self, key):
        self.shift = Vector2(0, 0)

        if key in ('1st_case', 'new_case'):
            phrase = self.assets.thoughts[key]
            text_to_render = phrase.format(self.assets.clue_to_text(self.director.investigated_clues[0]))
        elif key == None:
            return
        else:
            text_to_render = self.assets.thoughts[key]
        name_to_render = 'YOU:'

        self.text_image = text_mono.render_text(text_to_render, self.assets.tile_font, 1, self.render_window.x)
        self.label_image = None
        self.name_image = text_mono.render_text(name_to_render, self.assets.tile_font, 1, None, settings.pico_green)

        self.show_player_thoughts = True


    def update(self):
        if self.parent.fade.finished_out:
            if self.director.game_ended:
                if DEBUG: print('>> GAME ENDED')
                self.director.go_to('Titles', {})
                return

        if self.show_npc_talks:
            if self.key_control.up:
                if self.shift.y > 0:
                    if DEBUG: print('DBox ^')
                    self.shift.y -= 1
                    self.parent.assets.sounds['scroll'].play()
                    self.key_control.clear_keys()

            if self.key_control.down:
                if self.shift.y < (self.text_image.get_height()//TS)-self.render_window.y:
                    if DEBUG: print('DBox V')
                    self.shift.y += 1
                    self.parent.assets.sounds['scroll'].play()
                    self.key_control.clear_keys()

            if self.key_control.x:
                if DEBUG: print('DIALOGUE ENDED')
                if self.conv_npc.npc_scene_name == 'boss':
                    if self.director.game_ended:
                        # Перейти к Титрам
                        if self.director.show_end_dialog:
                            # Включить фейдаут сцены
                            self.parent.fade.fade_out()
                            self.director.cut_scene = True
                            self.parent.key_control.clear_keys()

                        # Включить диалог 'end' у босса сразу же за концом предыдущего диалога 'win'
                        else:
                            self.director.show_end_dialog = True
                            self.show_talks(self.parent.boss, 'end')

                            self.parent.start_spawning_coins = True

                            self.director.cut_scene = True

                            self.parent.boss.state = ActorState.TALK
                            self.parent.player.state = ActorState.IDLE

                            self.parent.player.key_control.clear_keys()
                            self.parent.key_control.clear_keys()
                            return

                    # Выдать первое задание
                    if not self.director.case_given:
                        if self.director.start_scene:
                            self.director.start_scene = False
                        self.director.case_given = True
                        self.director.current_thought = '1st_case'

                        self.director.questions['BossBriefroom'] = False
                        self.director.questions['Corridor'][0] = True
                        self.director.questions['Corridor'][2] = True
                        self.director.questions['Archive'] = True
                        self.director.questions['Office'] = True

                # Создать все, относящееся к новому ikit, если притащил DutyOfficerу фоторобот
                if self.conv_npc.npc_scene_name == 'dutyofficer' and self.director.case_given:
                    if self.director.ikit_made != settings.IKIT_ZERO:
                        print('DB-player-made ikit')
                        self.director.current_thought = '1st_ikit_send_out'
                        self.director.player_indicator = None
                        self.parent.player_indicator.set_item_type(self.director.player_indicator)

                        self.director.curr_ikit_npcs = self.director.npcgen.gen_current_ikit_npcs(self.director.ikit_made)
                        self.director.refresh_npcs_on_new_ikit()

                        self.director.ikit_try = settings.IKIT_ZERO
                        self.director.ikit_made = settings.IKIT_ZERO

                        self.director.questions['Corridor'][0] = False
                        self.director.questions['Corridor'][1] = True
                        self.director.questions['Corridor'][2] = False
                        self.director.questions['Office'] = False
                        self.director.questions['Archive'] = False
                        self.director.questions['Entrance'] = False

                if self.conv_npc.npc_scene_name == 'dutyofficer' and self.director.start_scene:
                    self.director.current_thought = 'start2'
                    self.director.player_indicator = None

                if self.conv_npc.npc_scene_name == 'witness':
                    if not self.conv_npc.refuse_to_talk:
                        clue = self.conv_npc.ikit_parts['assigned_hint'][0]
                        clue_part = self.conv_npc.ikit_parts['ikit_part']
                        if clue not in self.director.investigated_clues:
                             self.director.investigated_clues.append(clue)
                             # self.director.investigated_main_hints[clue_part] = self.conv_npc.ikit_parts # интереснее, когда не добавляется подсказка напрямую
                        else:
                            if self.director.investigated_main_hints[clue_part] == None:
                                self.director.investigated_main_hints[clue_part] = self.conv_npc.ikit_parts
                        if DEBUG: print('Dbox:')
                        if DEBUG: print('<!> Inv. main hints:', self.director.investigated_main_hints)
                        if DEBUG: print('<!> Inv. main clues:', self.director.investigated_clues)

                        if len(self.director.investigated_clues) == 4:
                            if DEBUG: print('<!> All clues investigated')
                            self.director.all_clues_investigated = True

                        if all(list(self.director.investigated_main_hints.values())):
                            if DEBUG: print('<!> All main hints investigated')
                            self.director.all_hints_investigated = True

                        self.parent.assets.sounds['yes_interr'].play()
                        self.conv_npc.refuse_to_talk = True

                self.conv_npc.state = ActorState.IDLE

                self.parent.top_black.show = False
                self.parent.bottom_black.show = False
                self.director.cut_scene = False

                if self.conv_npc.npc_scene_name == 'witness':
                    if self.conv_npc.refuse_to_talk:
                        self.parent.assets.sounds['confirm'].play()
                else:
                    self.parent.assets.sounds['confirm'].play()

                self.show_npc_talks = False
                self.conv_npc = None

                self.show_thoughts(self.director.current_thought)
                self.key_control.clear_keys()


        if self.show_player_thoughts:
            if self.key_control.up:
                if self.shift.y > 0:
                    if DEBUG: print('DB ^')
                    self.shift.y -= 1
                    self.parent.assets.sounds['scroll'].play()
                    self.key_control.clear_keys()

            if self.key_control.down:
                if self.shift.y < (self.text_image.get_height()//TS)-self.render_window.y:
                    if DEBUG: print('DB V')
                    self.shift.y += 1
                    self.parent.assets.sounds['scroll'].play()
                    self.key_control.clear_keys()


    def render(self, surface):
        if self.show_npc_talks or self.show_player_thoughts:
            if (self.text_image.get_height()//TS) > self.render_window.y:
                subsurface = self.text_image.subsurface(pygame.Rect(0, TS*self.shift.y, TS*self.render_window.x, TS*self.render_window.y))
            else:
                subsurface = self.text_image.subsurface(pygame.Rect(0, TS*self.shift.y, TS*self.render_window.x, TS*(self.text_image.get_height()//TS)))

            surface.blit(subsurface, self.pos)
            surface.blit(self.name_image, (0, TS*10))
            surface.blit(self.dash_image, (0, TS*11))
            if self.label_image != None:
                surface.blit(self.label_image, (TS*7, TS*16))

            if (self.text_image.get_height()//TS) > self.render_window.y:
                if self.shift.y > 0:
                    surface.blit(self.assets.labels['up'], (TS*13, TS*15))
                if self.shift.y < (self.text_image.get_height()//TS)-self.render_window.y:
                    surface.blit(self.assets.labels['down'], (TS*14, TS*15))








class CutSceneBlackBox(pygame.sprite.Sprite):

    def __init__(self, parent, pos, move_dir):
        super().__init__()

        self.parent = parent

        self.image = pygame.Surface((TS*16, TS*5))
        self.image.fill(pygame.Color('black'))

        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.center_y = pos.y
        self.y_cff = 3
        self.move_dir = move_dir

        self.show = False


    def update(self):
        player = self.parent.player

        if self.show:
            if self.move_dir == Vector2(0, 1):
                self.center_y += (player.rect.top-TS*7-self.center_y)/self.y_cff
            else:
                self.center_y += (player.rect.top+TS-self.center_y)/self.y_cff

        else:
            if self.move_dir == Vector2(0, 1):
                self.center_y += (self.pos.y-self.center_y)/self.y_cff
            else:
                self.center_y += (self.pos.y-self.center_y)/self.y_cff

        self.rect.topleft = Vector2(round(self.pos.x), round(self.center_y))


    def render(self, surface):
        surface.blit(self.image, self.rect)




class ClosingDoor(pygame.sprite.Sprite):

    def __init__(self, parent, pos):
        super().__init__()

        self.parent = parent

        self.image = parent.assets.closing_door_img
        self.pos = pos
        self.rect = self.image.get_rect(topleft = self.pos)

        self.center_y = pos.y
        self.y_cff = 30


    def update(self):
        if self.parent.close_door:
            self.center_y += (TS*5-self.center_y)/self.y_cff

        self.rect.topleft = Vector2(round(self.pos.x), round(self.center_y))


    def render(self, surface):
        surface.blit(self.image, self.rect)











class Particle(pygame.sprite.Sprite):

    def __init__(self, parent, pos, vel):
        super().__init__()

        self.parent = parent
        self.pos = pos
        self.vel = vel

        self.alpha = 255

        self.age = 0
        self.max_age = random.uniform(18.5, 21.5)
        self.aging_speed = random.uniform(16.5, 18.2)
        self.speed = random.uniform(0.4, 0.9)

        self.image = self.parent.steam_imgs[0]
        self.image.set_alpha(self.alpha)

        self.rect = self.image.get_rect(topleft=pos)


    def update(self, delta):
        self.pos += self.vel
        self.rect.topleft = self.pos

        self.age += delta
        self.alpha = int(255*(1-(self.age*self.aging_speed/self.max_age)))

        if self.alpha <= 204 and self.alpha > 153:
            self.image = self.parent.steam_imgs[1]
        elif self.alpha <= 153 and self.alpha > 102:
            self.image = self.parent.steam_imgs[2]
        elif self.alpha <= 102 and self.alpha > 51:
            self.image = self.parent.steam_imgs[3]
        elif self.alpha <= 51:
            self.image = self.parent.steam_imgs[4]

        if self.alpha > 0:
            self.image.set_alpha(self.alpha)
        else:
            self.kill()


class ParticleEmitter(object):

    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos
        self.particles = pygame.sprite.Group()

        self.steam_imgs = self.parent.assets.cond_steam_imgs

        self.spawn_timer = 2
        self.emit_start = False


    def add_particle(self):
        vel = Vector2(random.uniform(0.1, 0.2)*random.choice([-1, 1]), random.uniform(0.05, 0.13))
        p = Particle(self, Vector2(self.pos.x, self.pos.y), vel)

        self.particles.add(p)


    def update(self, delta):
        if self.emit_start:
            if self.spawn_timer >= 0:
                self.spawn_timer -= 1

                if self.spawn_timer == 0:
                    self.spawn_timer = random.randint(14, 30)
                    self.add_particle()

        self.particles.update(delta)


    def render(self, surface):
        self.particles.draw(surface)






class FloatingImage(pygame.sprite.Sprite):

    def __init__(self, parent, pos, image, flow_to_point=None, sin_pars=(0.2, 8, 0)):
        self._layer = 5

        super().__init__()

        self.parent = parent

        self.image_to_show = image

        self.no_image = pygame.Surface((TS, TS))
        self.no_image.set_colorkey(pygame.Color('magenta'))
        self.no_image.fill(pygame.Color('magenta'))

        self.image = self.no_image
        self.pos = pos
        self.pos_rect = self.no_image.get_rect(topleft = pos)

        self.rect = self.pos_rect.copy()
        self.rect.topleft = self.pos_rect.topleft

        self.center_y = pos.y
        self.y_cff = 6

        self.ampl = sin_pars[0]
        self.freq = sin_pars[1]
        self.phase = sin_pars[2]
        self.time = 0 # pygame.time.get_ticks()

        self.show = False

        self.flow_to_point = flow_to_point
        self.flow_to = False


    def update(self, delta):
        if self.show:
            self.image = self.image_to_show
        else:
            self.image = self.no_image

        self.pos.y += math.sin(math.radians(self.freq*self.time + self.phase)) * self.ampl

        if self.flow_to:
            self.center_y += (self.flow_to_point.y-self.center_y)/self.y_cff
            self.pos_rect.topleft = Vector2(round(self.pos.x), round(self.center_y))
            self.rect.topleft = self.pos_rect.topleft
        else:
            self.rect.topleft = Vector2(round(self.pos.x), round(self.pos.y))

        self.time += 1


    def render(self, surface):
        surface.blit(self.image, self.rect)
