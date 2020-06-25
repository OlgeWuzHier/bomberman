import os
import sys

import pygame
import numpy
import time

import assets
import constants
import characters

X_CHANGE = {
    pygame.K_LEFT: -1,
    pygame.K_RIGHT: +1,
}

Y_CHANGE = {
    pygame.K_UP: -1,
    pygame.K_DOWN: +1,
}


class Game:
    def __init__(self, screen, player):
        self.over = 0
        self.level = 1
        self.screen = screen
        self.screen_buffor = pygame.Surface((constants.FIELD_WIDTH,
                                             constants.FIELD_HEIGHT)).convert()
        self.player = player
        self.hard_blocks = pygame.sprite.Group(
                            [characters.HardBlock(x, y) for (x, y, cell)
                             in assets.Assets.get_tiles() if cell == "#"])
        self.soft_blocks = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.blasts = pygame.sprite.Group()

    def initialize_map(self):
        soft_block_count = 52 + self.level * 2
        free_tiles = [t for t in assets.Assets.get_tiles() if t[2] == " " or t[2] == "."]

        # Randomize places for soft blocks
        locations = numpy.ones(len(free_tiles))
        locations[soft_block_count:] = 0
        numpy.random.shuffle(locations)

        # Create list of soft blocks in already randomized positions and add to sprite group
        self.soft_blocks = pygame.sprite.Group(
                            [characters.SoftBlock(tile[0], tile[1]) for (location, tile)
                             in zip(locations, free_tiles) if location])

    def draw(self):
        self.soft_blocks.draw(self.screen_buffor)
        self.hard_blocks.draw(self.screen_buffor)
        self.bombs.draw(self.screen_buffor)
        self.player.draw(self.screen_buffor)

        # Blit buffor to screen
        blit_start_x = 0
        player_x = self.player.rect.x + constants.SPRITE_SIZE / 2

        if player_x > constants.WINDOW_WIDTH / 2:
            blit_start_x = -player_x + constants.WINDOW_WIDTH / 2
        if player_x > constants.FIELD_WIDTH - constants.WINDOW_WIDTH / 2:
            blit_start_x = -constants.FIELD_WIDTH + constants.WINDOW_WIDTH

        self.screen.blit(self.screen_buffor, (blit_start_x, 2 * constants.SPRITE_SIZE))

    def move_player(self):
        moved = False
        pressed = pygame.key.get_pressed()
        blocks = pygame.sprite.Group(self.hard_blocks.sprites() + self.soft_blocks.sprites())
        for key, direction in X_CHANGE.items():
            if pressed[key]:
                self.player.rect.x += direction * self.player.speed
                moved = True
                test_rect = pygame.sprite.spritecollide(self.player, blocks, False)
                if test_rect:
                    self.player.rect.x -= direction * self.player.speed
                    moved = False
                    if len(test_rect) == 1 and self.player.rect.top % constants.SPRITE_SIZE != 0:
                        top_point    = (self.player.rect.center[0] + direction * constants.SPRITE_SIZE, self.player.rect.top)
                        bottom_point = (self.player.rect.center[0] + direction * constants.SPRITE_SIZE, self.player.rect.bottom)
                        collision_top    = test_rect[0].rect.collidepoint(top_point)
                        collision_bottom = test_rect[0].rect.collidepoint(bottom_point)
                        if collision_top and not collision_bottom:
                            # TODO: better alignment
                            self.player.rect.y += self.player.speed
                            moved = True
                        elif not collision_top and collision_bottom:
                            self.player.rect.y -= self.player.speed
                            moved = True

        if not moved:
            for key, direction in Y_CHANGE.items():
                if pressed[key]:
                    self.player.rect.y += direction * self.player.speed
                    test_rect = pygame.sprite.spritecollide(self.player, blocks, False)
                    if test_rect:
                        self.player.rect.y -= direction * self.player.speed
                        if len(test_rect) == 1 and self.player.rect.left % constants.SPRITE_SIZE != 0:
                            left_point  = (self.player.rect.left,  self.player.rect.center[1] + direction * constants.SPRITE_SIZE)
                            right_point = (self.player.rect.right, self.player.rect.center[1] + direction * constants.SPRITE_SIZE)
                            collision_left  = test_rect[0].rect.collidepoint(left_point)
                            collision_right = test_rect[0].rect.collidepoint(right_point)
                            if collision_left and not collision_right:
                                self.player.rect.x += self.player.speed
                            elif not collision_left and collision_right:
                                self.player.rect.x -= self.player.speed

    def update(self):
        self.move_player()
        self.place_bomb()
        # Update sprites
        self.player.update()
        self.bombs.update()
        self.soft_blocks.update()
        self.hard_blocks.update()

    def clear(self):
        self.screen.fill(constants.BACKGROUND_COLOR)
        self.screen_buffor.fill(constants.FIELD_COLOR,
                                rect=pygame.Rect((0, 0),
                                                 (constants.FIELD_WIDTH, constants.FIELD_HEIGHT)))

    def place_bomb(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            if self.player.max_bombs > len(self.bombs.sprites()):
                self.bombs.add(characters.Bomb(self.player.get_tile_pos(),
                                               self.player.blast_range,
                                               self.blasts,
                                               self.hard_blocks,
                                               self.soft_blocks))



def main():
    # initialization
    pygame.init()
    pygame.display.set_caption("Bomberman")  # set the window title
    # pygame.mouse.set_visible(False)  # hide the mouse
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window

    # making necessary objects
    screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    assets.Assets.load()
    player_tile = next(t for t in assets.Assets.get_tiles() if t[2] == "o")
    player = characters.Player(player_tile[0], player_tile[1])
    game = Game(screen, player)
    game.initialize_map()

    # main game loop
    while not game.over:
        start_time = time.time()
        game.clear()
        game.update()
        game.draw()
        pygame.event.pump()
        pygame.display.update()
        # wait for duration of tick minus time used to process code above
        pygame.time.wait(int(constants.TICK_TIME_MS - 1000 * (time.time() - start_time)))

    # collecting the garbage
    pygame.display.quit()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()



