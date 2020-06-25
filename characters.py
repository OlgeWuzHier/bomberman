import pygame

import constants
import assets


class Character:
    def __init__(self):
        pass

    def draw(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented


class Enemy(Character):
    pass


class Blast(pygame.sprite.Sprite):
    def __init__(self, start_pos, type, rotation):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(0, 3)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE
        self.frame = 0
        self.timer = constants.BLAST_TIME

    def kill(self):

        pygame.sprite.Sprite.kill(self)

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.kill()
        # Update image frame
        self.frame = (self.frame + constants.ANIMATION_SPEED) % 4
        # Update image according to frame
        image_x, image_y = constants.BOMB_TICKING_ANIMATION[int(self.frame)]
        self.image = assets.Assets.get_image_at(image_x, image_y)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, start_pos, range, blasts, hard_blocks, soft_blocks):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(0, 3)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE
        self.frame = 0
        self.timer = constants.BOMB_TIME
        self.blasts = blasts
        self.range = range
        self.hard_blocks = hard_blocks
        self.soft_blocks = soft_blocks

    def kill(self):
        for direction in constants.Direction:
            print(direction)
        pygame.sprite.Sprite.kill(self)

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.kill()
        # Update image frame
        self.frame = (self.frame + constants.ANIMATION_SPEED) % 4
        # Update image according to frame
        image_x, image_y = constants.BOMB_TICKING_ANIMATION[int(self.frame)]
        self.image = assets.Assets.get_image_at(image_x, image_y)


class Block(pygame.sprite.Sprite):
    def __init__(self, image_pos, start_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(image_pos[0], image_pos[1])
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE


class HardBlock(Block):
    def __init__(self, start_x, start_y):
        super().__init__((3, 3), (start_x, start_y))


class SoftBlock(Block):
    def __init__(self, start_x, start_y):
        super().__init__((4, 3), (start_x, start_y))


class Player(pygame.sprite.Sprite):
    """Class representing the Bomberman himself."""
    def __init__(self, start_x, start_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(1, 1)
        self.rect = self.image.get_rect()
        self.rect.x = start_x * constants.SPRITE_SIZE
        self.rect.y = start_y * constants.SPRITE_SIZE
        self.frame = 1
        self.direction = constants.Direction.RIGHT
        self.speed = constants.BASE_SPEED
        self.__max_bombs = 1
        self.__blast_range = 1

    @property
    def blast_range(self):
        return self.__blast_range

    @blast_range.setter
    def blast_range(self, blast_range):
        if blast_range >= 5:
            self.__blast_range = 5

    @property
    def max_bombs(self):
        return self.__max_bombs

    @max_bombs.setter
    def max_bombs(self, max_bombs):
        if max_bombs >= 10:
            self.__max_bombs = 10

    def update(self):
        # Update image direction and frame
        pressed = pygame.key.get_pressed()
        keys = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_UP]
        for key in keys:
            if pressed[key]:
                self.direction = keys.index(key)
                self.frame = (self.frame + constants.ANIMATION_SPEED) % 4
                break  # so that animation's speed isn't doubled

        # Update image according to frame and direction
        image_x, image_y = constants.BOMBERMAN_MOVEMENT_ANIMATION[self.direction][int(self.frame)]
        self.image = assets.Assets.get_image_at(image_x, image_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_tile_pos(self):
        return self.rect.center[0] // constants.SPRITE_SIZE, self.rect.center[1] // constants.SPRITE_SIZE


class Ballom(Enemy):
    """The easiest enemy of them all. Slow and passive.

    Ballom has a very unpredictable movement pattern. They are slow and won't chase after
    Bomberman, but they turn or reverse direction upon colliding with a wall or bomb."""


class Onil(Enemy):
    """Medium-difficulty enemy. Quite quick, might chase after player.

    Onil moves quickly and randomly. They will move towards Bomberman when he is nearby. They
    are not likely to get stuck on walls and can be incredibly troublesome."""
    pass


class Dahl(Enemy):
    """Very easy opponent. Slow and passive, prone to stucking into walls.

    It moves at slightly fast speed, doing some bouncy moves (it doesn't jump however). It is
    not hard to kill since they are not smart, even less intelligent than Balloms and won't
    try to chase Bomberman. They prefer to move from left to right, sometimes switching to up
    and down. Commonly get stuck in walls."""
    pass


class Minvo(Enemy):
    """Medium-difficulty enemy. Quick and chasing.

    They move as fast as Onils. Encountered after the Dahls. They will pursue Bomberman if he's
    nearby, but commonly get stuck if he's hiding."""
    pass


class Doria(Enemy):
    """Difficult enemy. Quick, chasing, evading blocks and flying over Soft Blocks.

    It moves really slow, but it can move through Soft Blocks. It appears cyan-colored, just as
    the Onils are. Dorias are very smart, they will commonly attempt to chase Bomberman and they
    can evade bombs."""
    pass


class Ovape(Enemy):
    """Quite difficult enemy. They can fly over Soft Blocks.

    They resemble red, purple or pink ghosts that move through Soft Blocks. They are encountered
    after the Dorias They don't chase after Bomberman too commonly, unlike Dorias, but due to
    their wall-pass abilities, they can cause problems."""
    pass


class Tiglon(Enemy):
    """Difficult enemy. Very fast, evading and chasing.

    Tiglon moves faster than most enemies, and is able to avoid bombs. It often pursues Bomberman.
    Their behavior and appearance is kind of similar to Minvos. Unlike Minvos, however, they're
    a bit faster and smarter. They're associated with the Fireproof Power-up and as such, will
    appear if said power up is blown up by a bomb, or the exit of a level with this power up
    present is bombed."""
    pass


class Pontan(Enemy):
    """The most difficult enemy in the game. Fast, passing through Soft Blocks and chasing.

    Pontan moves very quickly, passing through Soft Blocks and constantly pursuing the player.
    They're associated with the Invincibility Power-up and as such, will appear if said power up
    is blown up by a bomb, or the exit of a level with this power up present is bombed or if the
    timer reaches zero. They are able to chase the player from one side of the screen to the other."""
    pass
