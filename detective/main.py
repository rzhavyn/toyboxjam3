import os
import sys
import math

import pygame

import director
import settings


def main_loop():
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.mixer.pre_init(22050, -16, 2, 1024)

    pygame.init()
    display_surface = pygame.display.set_mode((settings.app.END_WIN_W, settings.app.END_WIN_H))
    clock = pygame.time.Clock()
    fps = settings.app.FPS
    delta_time = 0
    ticks = 0

    game_director = director.Director()

    while game_director.game_running:
        clock.tick(fps)
        delta_time = (pygame.time.get_ticks() - ticks) / 1000.0 # перевод из мс в с
        ticks = pygame.time.get_ticks()

        if pygame.event.get(pygame.QUIT):
            game_director.game_running = False
            pygame.quit()
            sys.exit()
            return

        game_director.current_scene.handle_events(pygame.event.get())
        game_director.current_scene.update(delta_time)
        game_director.current_scene.render(display_surface)

        pygame.display.update()

        caption = '{} {} / FPS: {}'.format(settings.app.CAPTION, settings.app.VERSION,
                                           math.ceil(clock.get_fps()))
        pygame.display.set_caption(caption)


if __name__ == '__main__':
    main_loop()
