import math

import pygame

import settings

DEBUG = settings.DEBUG

def generate_font(font_dict):
    font_data = {}

    # Последовательность символов (font_order = font_dict по кол-ву символов)
    font_order = [' ','!','"','#','$','%','&','\'','(',')','*','+',',','-','.','/',
                  '0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?',
                  '@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O',
                  'P','Q','R','S','T','U','V','W','X','Y','Z','[','\\',']','^','_',
                  'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u', # 21 иконок зацепок
                  'À','Á','Â','Ã','Ä','Å','Æ','Ç','È','É','Ê','Ë','Ì','Í','Î','Ï','Ð','Ñ','Ò','Ó','Ô','Õ','Ö','×','Ø','Ù'] # 26 символов PICO8

    # Ширина и высота каждого символа (PICO-8 - моноширинный)
    font_data['size'] = 8

    # Заполнить font_data
    for i in range(len(font_order)):
        if i <= 63: # буквы и символы
            symbol = font_dict[i]
            surf = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            symbol.set_colorkey(settings.pico_light_gray)
            surf.blit(symbol, (0, 0))

            # # Залить одним цветом буквы
            # surf2 = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # surf2.fill(settings.pico_cyan)
            # surf.set_colorkey(settings.pico_white)
            # surf2.blit(surf, (0, 0))

            # # На темно-серой полосе
            # symbol = font_dict[i]
            # surf = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # symbol.set_colorkey(settings.pico_light_gray)
            # surf.blit(symbol, (0, 0))

            # # Только белый цвет букв
            # symbol = font_dict[i]
            # surf = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # symbol.set_colorkey(settings.pico_light_gray)
            # surf.blit(symbol, (0, 0))
            #
            # surf2 = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # surf2.fill(settings.pico_dark_gray)
            # surf.set_colorkey(settings.pico_dark_gray)
            # surf2.blit(surf, (0, 0))

            font_data[font_order[i]] = surf
        else:
            font_data[font_order[i]] = font_dict[i]

    return font_data


def render_text(text, font, scale, line_width_chars=None, color=None):
    text += '\n' # добавить в конце перенос на новую строку
    current_word = ''
    current_line_len = 0
    x = 0
    y = 0

    # Расчет размеров text_surf по text
    text_w = 0
    text_h = font['size']

    if line_width_chars != None:
        text_w = int(line_width_chars*font['size'])
        for char in text:
            if char not in ('\n', ' '):
                current_word += char
            else:
                free_space = int(line_width_chars)-current_line_len
                cw_space = current_word+' '
                if free_space >= len(current_word):
                    current_line_len += len(cw_space)
                else:
                    current_line_len = len(cw_space)
                    text_h += font['size']

                current_word = ''

    else:
        for char in text:
            if char != '\n':
                text_w += font['size']
            else:
                text_h += font['size']

    text_surf = pygame.Surface((text_w*scale, text_h*scale)).convert()
    text_surf.set_colorkey(pygame.Color('black'))

    if DEBUG: print('SIZE:', text_w, text_h)

    current_word = ''
    current_line_len = 0

    # Рендер надписи text на surface
    if line_width_chars != None:
        for char in text:
            if char not in ('\n', ' '):
                current_word += str(char)
            else:
                if DEBUG: print('CW:', current_word)
                free_space = int(line_width_chars)-current_line_len
                if DEBUG: print('\tfree space:', free_space)

                # cw_space = current_word+' '

                if free_space >= len(current_word): #len(cw_space):
                    current_line_len += len(current_word) #len(cw_space)
                    if DEBUG: print('\t\tcurrent_line_len:', current_line_len, '; render word...')
                    for word_char in current_word: #cw_space:
                        if DEBUG: print('\t\t\t', word_char)
                        image = font[str(word_char)].copy()
                        if color != None:
                            # Выделение текста цветом
                            img_colored = pygame.Surface((image.get_width(), image.get_height())).convert()
                            img_colored.fill(color)
                            image.set_colorkey(settings.pico_white)
                            img_colored.blit(image, (0, 0))
                            text_surf.blit(pygame.transform.scale(img_colored, (img_colored.get_width()*scale, img_colored.get_height()*scale)), (x*scale, y*scale))
                        else:
                            text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                        x += font['size']

                    # пробел между словами
                    image = font[str(' ')].copy()
                    text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                    x += font['size']
                    current_line_len += 1

                else:
                    # if DEBUG: print('\t\tfree_space', free_space, '< cw_space', len(cw_space))
                    if DEBUG: print('\t\tfree_space', free_space, '< current_word', len(current_word))
                    if DEBUG: print('\t\tappend line with spaces')
                    for i in range(free_space):
                        image = font[str(' ')].copy()
                        text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                        x += font['size']

                    if DEBUG: print('\t\tgo new line')
                    # current_line_len = len(cw_space)
                    current_line_len = len(current_word)
                    x = 0
                    y += font['size']

                    if DEBUG: print('\t\trender word on new line...')
                    for word_char in current_word: #cw_space:
                        if DEBUG: print('\t\t\t', word_char)
                        image = font[str(word_char)].copy()
                        if color != None:
                            # Выделение текста цветом
                            img_colored = pygame.Surface((image.get_width(), image.get_height())).convert()
                            img_colored.fill(color)
                            image.set_colorkey(settings.pico_white)
                            img_colored.blit(image, (0, 0))
                            text_surf.blit(pygame.transform.scale(img_colored, (img_colored.get_width()*scale, img_colored.get_height()*scale)), (x*scale, y*scale))
                        else:
                            text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                        x += font['size']

                    # пробел между словами
                    image = font[str(' ')].copy()
                    text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                    x += font['size']
                    current_line_len += 1

                current_word = ''

    else:
        for char in text:
            if char not in ('\n', ' '):
                current_word += str(char)
            else:
                cw_space = current_word+' '

                for word_char in cw_space:
                    image = font[str(word_char)].copy()
                    if color != None:
                        # Выделение текста цветом
                        img_colored = pygame.Surface((image.get_width(), image.get_height())).convert()
                        img_colored.fill(color)
                        image.set_colorkey(settings.pico_white)
                        img_colored.blit(image, (0, 0))
                        text_surf.blit(pygame.transform.scale(img_colored, (img_colored.get_width()*scale, img_colored.get_height()*scale)), (x*scale, y*scale))
                    else:
                        text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                    x += font['size']

                if char == '\n':
                    x = 0
                    y += font['size']

                current_word = ''

    return text_surf
