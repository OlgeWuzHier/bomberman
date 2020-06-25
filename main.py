import os
import sys

import pygame
import numpy
import time

import assets
import constants
import characters


class Game:
    def __init__(self, screen, player):
        self.over = 0
        self.level = 1
        self.screen = screen
        self.screen_buffor = pygame.Surface((constants.FIELD_WIDTH,
                                             constants.FIELD_HEIGHT)).convert()
        self.player = player
        self.hard_blocks = []
        self.soft_blocks = []

    def initialize_map(self):
        self.hard_blocks = []
        self.soft_blocks = []
        for x, y, cell in assets.Assets.get_tiles():
            if cell == "#":
                self.hard_blocks.append((x, y))
        soft_block_count = 52 + self.level * 2
        # Non hard-block tiles
        free_tiles = [t for t in assets.Assets.get_tiles() if t[2] == " " or t[2] == "."]

        # Randomize places for soft blocks
        locations = numpy.ones(len(free_tiles))
        locations[soft_block_count:] = 0
        numpy.random.shuffle(locations)

        for location, tile in zip(locations, free_tiles):
            if location:
                self.soft_blocks.append((tile[0], tile[1]))

    def draw(self):
        # Draw player
        self.screen_buffor.blit(self.player.get_image(),
                                (self.player.x - 0.5 * constants.SPRITE_SIZE,
                                 self.player.y - 0.5 * constants.SPRITE_SIZE))
        # Draw hard blocks
        hard_block_image = assets.Assets.get_image_at(3, 3)
        for x, y in self.hard_blocks:
            self.screen_buffor.blit(hard_block_image,
                                    (x * constants.SPRITE_SIZE, y * constants.SPRITE_SIZE))
        # Draw soft blocks
        soft_block_image = assets.Assets.get_image_at(4, 3)
        for x, y in self.soft_blocks:
            self.screen_buffor.blit(soft_block_image,
                                    (x * constants.SPRITE_SIZE, y * constants.SPRITE_SIZE))

        # Blit buffor to screen
        blit_start_x = 0
        if self.player.x > constants.WINDOW_WIDTH / 2:
            blit_start_x = -self.player.x + constants.WINDOW_WIDTH / 2
        if self.player.x > constants.FIELD_WIDTH - constants.WINDOW_WIDTH / 2:
            blit_start_x = -constants.FIELD_WIDTH + constants.WINDOW_WIDTH

        self.screen.blit(self.screen_buffor, (blit_start_x, 2 * constants.SPRITE_SIZE))

    def move(self):
        self.player.move(self.soft_blocks, self.hard_blocks)

    def clear(self):
        self.screen.fill(constants.BACKGROUND_COLOR)
        self.screen_buffor.fill(constants.FIELD_COLOR,
                                rect=pygame.Rect((0, 0),
                                                 (constants.FIELD_WIDTH, constants.FIELD_HEIGHT)))


def main():
    # initialization
    pygame.init()
    pygame.display.set_caption("Bomberman")  # set the window title
    #pygame.mouse.set_visible(False)  # hide the mouse
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window

    # making necessary objects
    screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    assets.Assets.load()
    player_tile = next(t for t in assets.Assets.get_tiles() if t[2] == "o")
    player = characters.Player(player_tile[0], player_tile[1])
    game = Game(screen, player)
    game.initialize_map()
    # game's main loop
    while not game.over:
        start_time = time.time()
        game.clear()
        game.move()
        game.draw()
        pygame.event.pump()
        pygame.display.update()
        pygame.time.wait(int(constants.TICK_TIME_MS -  1000 * (time.time() - start_time)))  # wait for duration of tick minus time needed to proceed code above

    # collecting the garbage
    pygame.display.quit()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()



