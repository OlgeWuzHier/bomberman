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
        self.player = pygame.sprite.GroupSingle(player)
        self.hard_blocks = pygame.sprite.Group(
                            [characters.HardBlock(x, y) for (x, y, cell)
                             in assets.Assets.get_tiles() if cell == "#"])
        self.soft_blocks = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.blasts = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.time = 200 * constants.TICK_RATE
        self.score = 0

    def initialize_level(self, level):
        # Reset game variables
        self.bombs = pygame.sprite.Group()
        self.blasts = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.time = 200 * constants.TICK_RATE
        # Reset player variables
        self.player.sprite.dead = 0
        self.player.sprite.frame = 0
        player_tile = next(t for t in assets.Assets.get_tiles() if t[2] == "o")
        self.player.sprite.rect.x = player_tile[0] * constants.SPRITE_SIZE
        self.player.sprite.rect.y = player_tile[1] * constants.SPRITE_SIZE

        soft_block_count = 52 + level * 2
        free_tiles = [t for t in assets.Assets.get_tiles() if t[2] == " " or t[2] == "."]

        # Randomize places for soft blocks
        locations = numpy.ones(len(free_tiles))
        locations[soft_block_count:] = 0
        numpy.random.shuffle(locations)

        # Create list of soft blocks in already randomized positions and add to sprite group
        soft_block_locations = [(tile[0], tile[1]) for (location, tile)
                                in zip(locations, free_tiles) if location]
        self.soft_blocks = pygame.sprite.Group(
                            [characters.SoftBlock(tile[0], tile[1]) for tile in soft_block_locations])
        # Randomize places for monsters
        free_tiles = [(t[0], t[1]) for t in assets.Assets.get_tiles() if t[2] == " "]
        free_tiles = list(set(free_tiles) - set(soft_block_locations))
        numpy.random.shuffle(free_tiles)
        # Spawn monsters
        level_content = constants.LEVEL_CONTENT_LIST[level - 1]
        for monster_name, monster_count in enumerate(level_content[0]):
            for i in range(monster_count):
                self.monsters.add(characters.get_monster_by_name(monster_name,
                                                                 free_tiles.pop(),
                                                                 self.bombs,
                                                                 self.soft_blocks,
                                                                 self.hard_blocks))

    def draw(self):
        self.soft_blocks.draw(self.screen_buffor)
        self.hard_blocks.draw(self.screen_buffor)
        self.bombs.draw(self.screen_buffor)
        self.blasts.draw(self.screen_buffor)
        self.monsters.draw(self.screen_buffor)
        self.player.draw(self.screen_buffor)

        # Blit buffor to screen
        player = self.player.sprite
        blit_start_x = 0
        player_x = player.rect.x + constants.SPRITE_SIZE / 2

        if player_x > constants.WINDOW_WIDTH / 2:
            blit_start_x = -player_x + constants.WINDOW_WIDTH / 2
        if player_x > constants.FIELD_WIDTH - constants.WINDOW_WIDTH / 2:
            blit_start_x = -constants.FIELD_WIDTH + constants.WINDOW_WIDTH

        self.screen.blit(self.screen_buffor, (blit_start_x, 2 * constants.SPRITE_SIZE))

    def move_player(self):
        player = self.player.sprite
        if player.dead == 1:
            return
        moved = False
        pressed = pygame.key.get_pressed()
        blocks = pygame.sprite.Group(self.hard_blocks.sprites() + self.soft_blocks.sprites())
        for key, direction in X_CHANGE.items():
            if pressed[key]:
                player.rect.x += direction * player.speed
                moved = True
                test_rect = pygame.sprite.spritecollide(player, blocks, False)
                if test_rect:
                    player.rect.x -= direction * player.speed
                    moved = False
                    if len(test_rect) == 1 and player.rect.top % constants.SPRITE_SIZE != 0:
                        top_point    = (player.rect.center[0] + direction * constants.SPRITE_SIZE, player.rect.top)
                        bottom_point = (player.rect.center[0] + direction * constants.SPRITE_SIZE, player.rect.bottom)
                        collision_top    = test_rect[0].rect.collidepoint(top_point)
                        collision_bottom = test_rect[0].rect.collidepoint(bottom_point)
                        if collision_top and not collision_bottom:
                            # TODO: better alignment
                            player.rect.y += player.speed
                            moved = True
                        elif not collision_top and collision_bottom:
                            player.rect.y -= player.speed
                            moved = True

        if not moved:
            for key, direction in Y_CHANGE.items():
                if pressed[key]:
                    player.rect.y += direction * player.speed
                    test_rect = pygame.sprite.spritecollide(player, blocks, False)
                    if test_rect:
                        player.rect.y -= direction * player.speed
                        if len(test_rect) == 1 and player.rect.left % constants.SPRITE_SIZE != 0:
                            left_point  = (player.rect.left,  player.rect.center[1] + direction * constants.SPRITE_SIZE)
                            right_point = (player.rect.right, player.rect.center[1] + direction * constants.SPRITE_SIZE)
                            collision_left  = test_rect[0].rect.collidepoint(left_point)
                            collision_right = test_rect[0].rect.collidepoint(right_point)
                            if collision_left and not collision_right:
                                player.rect.x += player.speed
                            elif not collision_left and collision_right:
                                player.rect.x -= player.speed

    def update(self):
        self.time -= 1
        self.update_scoreboard()
        self.check_player_death()
        self.move_player()
        self.place_bomb()
        self.check_collisions()
        # Update sprites
        self.player.update()
        self.monsters.update()
        self.bombs.update()
        self.blasts.update()
        self.soft_blocks.update()
        self.hard_blocks.update()

    def clear(self):
        self.screen.fill(constants.BACKGROUND_COLOR)
        self.screen_buffor.fill(constants.FIELD_COLOR,
                                rect=pygame.Rect((0, 0),
                                                 (constants.FIELD_WIDTH, constants.FIELD_HEIGHT)))

    def place_bomb(self):
        player = self.player.sprite
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            if player.max_bombs > len(self.bombs.sprites()):
                if not pygame.sprite.spritecollide(player, self.bombs, False):
                    self.bombs.add(characters.Bomb(player.get_tile_pos(),
                                                   player.blast_range,
                                                   self.blasts,
                                                   self.hard_blocks,
                                                   self.soft_blocks))

    def check_collisions(self):
        pygame.sprite.groupcollide(self.monsters, self.player, False, True, pygame.sprite.collide_rect_ratio(0.7))
        pygame.sprite.groupcollide(self.blasts, self.monsters, False, True, pygame.sprite.collide_rect_ratio(0.7))
        pygame.sprite.groupcollide(self.blasts, self.player, False, True, pygame.sprite.collide_rect_ratio(0.7))

    def check_player_death(self):
        if self.player.sprite.dead == 1 and int(self.player.sprite.frame) == 7:
            if self.player.sprite.lives == -1:
                self.player.sprite.lives = 2
                # TODO: Reset bonuses here
                self.initialize_level(1)
            else:
                self.initialize_level(self.level)

    def update_scoreboard(self):
        font = assets.Assets.get_font()

        strings = [
            f"TIME {self.time // constants.TICK_RATE}",
            f"{self.score}",
            f"LIVES {self.player.sprite.lives}",
        ]

        for position, string in enumerate(strings):

            text = font.render(string, True, constants.WHITE_COLOR, constants.BACKGROUND_COLOR)
            text.set_colorkey(constants.BACKGROUND_COLOR)
            text_rect = text.get_rect()

            text_shadow = font.render(string, True, constants.BLACK_COLOR, constants.BACKGROUND_COLOR)
            text_shadow.set_colorkey(constants.BACKGROUND_COLOR)

            text_shadow_rect = text_shadow.get_rect()

            text_rect.top = constants.SPRITE_SIZE
            text_shadow_rect.top = constants.SPRITE_SIZE
            if position == 0:
                text_rect.x = constants.SPRITE_SIZE / 2
                text_shadow_rect.x = constants.SPRITE_SIZE / 2
            elif position == 1:
                text_rect.center = (constants.WINDOW_WIDTH / 2, text_rect.center[1])
                text_shadow_rect.center = (constants.WINDOW_WIDTH / 2, text_shadow_rect.center[1])
            elif position == 2:
                text_rect.right = constants.WINDOW_WIDTH - constants.SPRITE_SIZE / 2
                text_shadow_rect.right = constants.WINDOW_WIDTH - constants.SPRITE_SIZE / 2

            text_shadow_rect.x += 3
            text_shadow_rect.y += 1

            self.screen.blit(text_shadow, text_shadow_rect)
            self.screen.blit(text, text_rect)


def main():
    # initialization
    pygame.init()
    screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    assets.Assets.load()
    pygame.display.set_caption("Bomberman")  # set the window title
    pygame.display.set_icon(assets.Assets.get_image_at(0, 3))
    # pygame.mouse.set_visible(False)  # hide the mouse
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window

    # making necessary objects
    player_tile = next(t for t in assets.Assets.get_tiles() if t[2] == "o")
    player = characters.Player(player_tile[0], player_tile[1])
    game = Game(screen, player)
    game.initialize_level(1)

    # main game loop
    while not game.over:
        start_time = time.time()

        # enabling closing the window by system button
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.over = True

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



