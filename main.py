import copy
import os
import random
import sys

import tracemalloc
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
    def __init__(self, screen):
        # Game variables
        self.level = 1
        self.time = 200 * constants.TICK_RATE
        self.score = 0
        self.level_score = 0

        # Canvas-related variables
        self.screen = screen
        self.screen_buffor = pygame.Surface((constants.FIELD_WIDTH,
                                             constants.FIELD_HEIGHT)).convert()

        # In-game objects variables
        self.player = pygame.sprite.GroupSingle(characters.Player(0, 0))
        self.player_copy = None
        # Hardblocks (every "#" in gamemap), which remain the same through all levels
        self.hard_blocks = pygame.sprite.Group(
                            [characters.HardBlock((x, y)) for (x, y, cell)
                             in assets.Assets.get_tiles() if cell == "#"])
        self.soft_blocks = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.blasts = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

    def initialize_level(self, level):
        # Reset game variables (in case of leftovers from previous level/life)
        self.bombs = pygame.sprite.Group()
        self.blasts = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.time = 200 * constants.TICK_RATE
        self.level_score = 0
        # Reset player variables
        self.player.sprite.dead = 0
        self.player.sprite.frame = 0
        player_tile = next(t for t in assets.Assets.get_tiles() if t[2] == "o")
        self.player.sprite.rect.x = player_tile[0] * constants.SPRITE_SIZE
        self.player.sprite.rect.y = player_tile[1] * constants.SPRITE_SIZE
        self.player_copy = copy.copy(self.player.sprite)
        # How many soft blocks will be on the current level
        soft_block_count = 52 + level * 2
        free_tiles = [t for t in assets.Assets.get_tiles() if t[2] == " " or t[2] == "."]
        # Randomize places for soft blocks
        locations = numpy.ones(len(free_tiles))
        locations[soft_block_count:] = 0
        numpy.random.shuffle(locations)
        # Create list of soft blocks in already randomized positions and add to sprite group
        soft_block_locations = [(tile[0], tile[1]) for (location, tile)
                                in zip(locations, free_tiles) if location]
        numpy.random.shuffle(soft_block_locations)
        # Randomize places for monsters
        free_tiles = [(t[0], t[1]) for t in assets.Assets.get_tiles() if t[2] == " "]
        free_tiles = list(set(free_tiles) - set(soft_block_locations))
        numpy.random.shuffle(free_tiles)
        # Spawn soft_blocks with bonuses
        bonus_block = soft_block_locations.pop()
        exit_block = soft_block_locations.pop()
        self.soft_blocks = pygame.sprite.Group(
                            [characters.SoftBlock((tile[0], tile[1])) for tile in soft_block_locations])
        self.soft_blocks.add(characters.SoftBlock(bonus_block, bonus_type=constants.LEVEL_CONTENT_LIST[level - 1][1], bonuses=self.bonuses))
        self.soft_blocks.add(characters.SoftBlock(exit_block, bonus_type=constants.Bonus.EXIT, bonuses=self.bonuses))
        # Spawn monsters basing on the list from contants
        level_content = constants.LEVEL_CONTENT_LIST[level - 1]
        for monster_name, monster_count in enumerate(level_content[0]):
            for i in range(monster_count):
                self.monsters.add(characters.get_monster_by_name(monster_name,
                                                                 free_tiles.pop(),
                                                                 self.bombs,
                                                                 self.soft_blocks,
                                                                 self.hard_blocks))

    def draw(self):
        # Draw new frame on the buffor
        self.soft_blocks.draw(self.screen_buffor)
        self.hard_blocks.draw(self.screen_buffor)
        self.bombs.draw(self.screen_buffor)
        self.blasts.draw(self.screen_buffor)
        self.bonuses.draw(self.screen_buffor)
        self.monsters.draw(self.screen_buffor)
        self.player.draw(self.screen_buffor)

        # Blit buffor to screen
        player = self.player.sprite
        blit_start_x = 0
        player_x = player.rect.x + constants.SPRITE_SIZE // 2

        # Handling window scrolling (actually - not scrolling by the edges)
        if player_x > constants.WINDOW_WIDTH / 2:
            blit_start_x = -player_x + constants.WINDOW_WIDTH / 2
        if player_x > constants.FIELD_WIDTH - constants.WINDOW_WIDTH / 2:
            blit_start_x = -constants.FIELD_WIDTH + constants.WINDOW_WIDTH

        self.screen.blit(self.screen_buffor, (blit_start_x, 2 * constants.SPRITE_SIZE))

    def move_player(self):
        def spritegrouplistcollide(sprite, grouplist, dokill):
            collision_list = []
            for group in grouplist:
                collided = pygame.sprite.spritecollide(sprite, group, dokill)
                for item in collided:
                    collision_list.append(item)
            return collision_list


        player = self.player.sprite

        # Disabling moving the dead corpse :)
        if player.dead == 1:
            return

        moved = False
        pressed = pygame.key.get_pressed()
        # TODO adjusting block group according to wall-walker bonus
        blocks = [self.hard_blocks, self.soft_blocks]
        obstacles = [self.hard_blocks, self.soft_blocks, self.bombs]
        # Loop on left and right arrows
        for key, direction in X_CHANGE.items():
            if pressed[key]:
                if pygame.sprite.spritecollide(player, self.bombs, False):
                    player.rect.x += direction * player.speed
                    moved = True
                    if spritegrouplistcollide(player, blocks, False):
                        player.rect.x -= direction * player.speed
                        moved = False
                player.rect.x += direction * player.speed
                moved = True
                # Moving the player back if the collision occured
                if spritegrouplistcollide(player, obstacles, False):
                    test_rect = spritegrouplistcollide(player, blocks, False)
                    player.rect.x -= direction * player.speed
                    moved = False
                    # Aligning the player on the X axis so that he won't get stuck on crossings so often
                    if len(test_rect) == 1 and player.rect.top % constants.SPRITE_SIZE != 0:
                        # Two points - upper- and bottom-right/left (according to the direction) are checked for collision
                        top_point = (player.rect.center[0] + direction * constants.SPRITE_SIZE, player.rect.top)
                        bottom_point = (player.rect.center[0] + direction * constants.SPRITE_SIZE, player.rect.bottom)
                        collision_top = test_rect[0].rect.collidepoint(top_point)
                        collision_bottom = test_rect[0].rect.collidepoint(bottom_point)
                        # If the collision was only on one of the points - the player is aligned
                        if collision_top and not collision_bottom:
                            # TODO: better alignment
                            player.rect.y += player.speed
                            moved = True
                        elif not collision_top and collision_bottom:
                            player.rect.y -= player.speed
                            moved = True

        # X-axis moving is favoured to avoid some bugs
        if not moved:
            for key, direction in Y_CHANGE.items():
                if pressed[key]:
                    if pygame.sprite.spritecollide(player, self.bombs, False):
                        player.rect.y += direction * player.speed
                        if spritegrouplistcollide(player, blocks, False):
                            player.rect.y -= direction * player.speed
                    player.rect.y += direction * player.speed
                    if spritegrouplistcollide(player, obstacles, False):
                        test_rect = spritegrouplistcollide(player, blocks, False)
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

        # Align player to grid so that he can change directions
        dx = player.rect.x % constants.SPRITE_SIZE
        dy = player.rect.y % constants.SPRITE_SIZE
        if ((dx <= player.speed / 2 or dx >= constants.SPRITE_SIZE - player.speed / 2) and
            (dy <= player.speed / 2 or dy >= constants.SPRITE_SIZE - player.speed / 2)):
            player.rect.x = player.get_tile_pos()[0] * constants.SPRITE_SIZE
            player.rect.y = player.get_tile_pos()[1] * constants.SPRITE_SIZE

    def update(self):
        self.time -= 1
        self.update_scoreboard()
        self.check_player_death()
        self.move_player()
        self.place_bomb()
        self.detonate_remotely()
        self.check_collisions()

        # Update sprites
        self.player.update()
        self.monsters.update()
        self.bombs.update()
        self.blasts.update()
        self.bonuses.update()
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
                # Avoiding placing multiple bombs in one place
                if not pygame.sprite.spritecollide(player, self.bombs, False, pygame.sprite.collide_rect_ratio(0.8)):
                    self.bombs.add(characters.Bomb(player.get_tile_pos(),
                                                   player.blast_range,
                                                   self.blasts,
                                                   self.hard_blocks,
                                                   self.soft_blocks,
                                                   remote=player.detonator_bonus))

    def check_collisions(self):
        pygame.sprite.groupcollide(self.monsters, self.player, False, True, pygame.sprite.collide_rect_ratio(0.7))
        collected_bonus = pygame.sprite.groupcollide(self.player, self.bonuses, False, False, pygame.sprite.collide_rect_ratio(0.7))
        self.activate_bonus(collected_bonus)
        killed_monsters = pygame.sprite.groupcollide(self.blasts, self.monsters, False, False, pygame.sprite.collide_rect_ratio(0.7))
        self.add_points(killed_monsters)
        # TODO add invulnerability to bombs when having flame-proof or mystery bonus
        pygame.sprite.groupcollide(self.blasts, self.player, False, True, pygame.sprite.collide_rect_ratio(0.7))

    def check_player_death(self):
        if self.player.sprite.dead == 1 and int(self.player.sprite.frame) == 7:
            # Game Over, reseting the game
            if self.player.sprite.lives == -1:
                self.player.sprite.lives = 2
                self.player.sprite.max_bombs = 1
                self.player.sprite.blast_range = 1
                self.player.sprite.speed_bonus = False
                self.player.sprite.detonator_bonus = False
                self.score = 0
                self.initialize_level(1)
            # Restart the level with one life and bonuses other than bomb count, speed and blast range lost
            else:
                # Adding copy of player to GroupSingle - old one is removed
                self.player.add(self.player_copy)
                self.player.sprite.detonator_bonus = False
                self.score -= self.level_score
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
                text_rect.x = constants.SPRITE_SIZE // 2
                text_shadow_rect.x = constants.SPRITE_SIZE // 2
            elif position == 1:
                text_rect.center = (constants.WINDOW_WIDTH // 2, text_rect.center[1])
                text_shadow_rect.center = (constants.WINDOW_WIDTH // 2, text_shadow_rect.center[1])
            elif position == 2:
                text_rect.right = constants.WINDOW_WIDTH - constants.SPRITE_SIZE // 2
                text_shadow_rect.right = constants.WINDOW_WIDTH - constants.SPRITE_SIZE // 2

            text_shadow_rect.x += 3
            text_shadow_rect.y += 1

            self.screen.blit(text_shadow, text_shadow_rect)
            self.screen.blit(text, text_rect)

    def activate_bonus(self, collected_bonus):
        if len(collected_bonus) > 0:
            for bonuses in collected_bonus.values():
                for bonus in bonuses:
                    if bonus.bonus_type == constants.Bonus.EXTRA_BOMB:
                        self.player.sprite.max_bombs += 1
                    elif bonus.bonus_type == constants.Bonus.FIRE_RANGE:
                        self.player.sprite.blast_range += 1
                    elif bonus.bonus_type == constants.Bonus.SPEEDUP:
                        self.player.sprite.speed_bonus = True
                    elif bonus.bonus_type == constants.Bonus.WALL_WALKER:
                        pass
                    elif bonus.bonus_type == constants.Bonus.DETONATOR:
                        self.player.sprite.detonator_bonus = True
                    elif bonus.bonus_type == constants.Bonus.BOMB_WALKER:
                        pass
                    elif bonus.bonus_type == constants.Bonus.FLAME_PROOF:
                        pass
                    elif bonus.bonus_type == constants.Bonus.MYSTERY:
                        pass
                    elif bonus.bonus_type == constants.Bonus.EXIT:
                        if len(self.monsters.sprites()) == 0:
                            self.level += 1
                            self.initialize_level(self.level)
                    if bonus.bonus_type != constants.Bonus.EXIT:
                        bonus.kill()

    def detonate_remotely(self):
        if self.player.sprite.detonator_bonus:
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LCTRL, pygame.K_RCTRL]:
                        if len(self.bombs.sprites()) > 0:
                            self.bombs.sprites()[0].kill()

    def add_points(self, killed_monsters):
        if len(killed_monsters) > 0:
            for monsters in killed_monsters.values():
                for monster in monsters:
                    if not monster.dead:
                        self.score += monster.points
                        self.level_score += monster.points
                        monster.kill()


def main():
    # initialization
    tracemalloc.start(25)
    pygame.init()
    screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    assets.Assets.load()
    pygame.display.set_caption("Bomberman")  # set the window title
    pygame.display.set_icon(assets.Assets.get_image_at(0, 3)) # set the window icon
    # pygame.mouse.set_visible(False)  # hide the mouse
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window

    # making necessary objects
    game = Game(screen)
    game.initialize_level(3)

    # main game loop
    while True:
        start_time = time.time()

        # enabling closing the window by system button
        if pygame.QUIT in [event.type for event in pygame.event.get(pygame.QUIT)]:
            break

        game.clear()
        game.update()
        game.draw()
        pygame.event.pump()
        pygame.display.update()
        # wait for duration of tick minus time used to process code above
        pygame.time.wait(int(constants.TICK_TIME_MS - 1000 * (time.time() - start_time)))

    # tracemalloc
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')

    # pick the biggest memory block
    stat = top_stats[0]
    print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
    for line in stat.traceback.format():
        print(line)

    # sweeping
    pygame.display.quit()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
