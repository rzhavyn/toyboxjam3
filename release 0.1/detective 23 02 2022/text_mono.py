import math

import pygame

import settings

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
        if i <= 63:
            symbol = font_dict[i]
            surf = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # surf.fill(settings.pico_dark_gray) #
            symbol.set_colorkey(settings.pico_light_gray)
            surf.blit(symbol, (0, 0))

            # surf2 = pygame.Surface((symbol.get_width(), symbol.get_height())).convert()
            # surf2.fill(settings.pico_dark_gray)
            # surf.set_colorkey(settings.pico_dark_gray)
            # surf2.blit(surf, (0, 0))

            font_data[font_order[i]] = surf
        else:
            font_data[font_order[i]] = font_dict[i]

    return font_data


def render_text(text, font, scale, line_width_chars=0):
    text += '\n' # добавить в конце перенос на новую строку
    current_line = ''
    x = 0
    y = 0

    # Расчет размеров text_surf по text
    text_w = 0
    text_h = font['size']

    if line_width_chars != 0:
        text_w = line_width_chars*font['size']
        text_h = math.ceil(len(text)/line_width_chars)*font['size']

        # Рендер надписи text на surface
        text_surf = pygame.Surface((text_w*scale, text_h*scale)).convert()
        text_surf.set_colorkey(pygame.Color('black'))

        for char in text:
            if char != '\n' and len(current_line) != line_width_chars:
                image = font[str(char)]
                current_line += str(char)

            else:
                for line_char in current_line:
                    image = font[str(line_char)]
                    text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                    x += font['size']

                if char == '\n' or len(current_line) == line_width_chars:
                    x = 0
                    y += font['size']

                current_line = char

    else:
        for char in text:
            if char != '\n':
                image = font[str(char)]
                text_w += font['size']
            else:
                text_h += font['size']

        # Рендер надписи text на surface
        text_surf = pygame.Surface((text_w*scale, text_h*scale)).convert()
        text_surf.set_colorkey(pygame.Color('black'))

        for char in text:
            if char != '\n':
                image = font[str(char)]
                current_line += str(char)

            else:
                for line_char in current_line:
                    image = font[str(line_char)]
                    text_surf.blit(pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale)), (x*scale, y*scale))
                    x += font['size']

                if char == '\n':
                    x = 0
                    y += font['size']

                current_line = ''

    return text_surf
