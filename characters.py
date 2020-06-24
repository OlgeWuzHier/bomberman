import pygame

import constants
import assets

X_CHANGE = {
    pygame.K_LEFT: -1,
    pygame.K_RIGHT: +1,
}

Y_CHANGE = {
    pygame.K_UP: -1,
    pygame.K_DOWN: +1,
}


class Character:
    def __init__(self):
        self.speed = constants.BASE_SPEED

    def draw(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented


class Enemy(Character):
    pass


class Player(Character):
    """Class representing the Bomberman himself."""
    def __init__(self, start_x, start_y):
        super().__init__()
        self.x = (start_x + 0.5) * constants.SPRITE_SIZE
        self.y = (start_y + 0.5) * constants.SPRITE_SIZE
        self.frame = 1
        self.direction = constants.Direction.RIGHT

    def get_image(self):
        image_x, image_y = constants.BOMBERMAN_MOVEMENT_ANIMATION[self.direction][int(self.frame)]
        return assets.Assets.get_image_at(image_x, image_y)

    def move(self):
        pressed = pygame.key.get_pressed()
        keys = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_UP]

        for key, direction in X_CHANGE.items():
            if pressed[key]:
                self.x += direction * self.speed

        for key, direction in Y_CHANGE.items():
            if pressed[key]:
                self.y += direction * self.speed

        for key in keys:
            if pressed[key]:
                self.frame = (self.frame + constants.ANIMATION_SPEED) % 4
                self.direction = keys.index(key)
                break  # so that animation's speed isn't doubled



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
