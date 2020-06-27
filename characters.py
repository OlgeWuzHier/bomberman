import math
import random
import pygame

import constants
import assets


def get_modified_position(coordinates, direction, delta):
    """Returns modified coortinates by given direction and value"""
    current_x, current_y = coordinates
    (new_x, new_y) = {
        0: lambda x, y: (x - delta, y),  # LEFT
        1: lambda x, y: (x, y + delta),  # DOWN
        2: lambda x, y: (x + delta, y),  # RIGHT
        3: lambda x, y: (x, y - delta),  # UP
    }[direction](current_x, current_y)
    return new_x, new_y


def spritegrouplistcollide(sprite, grouplist, dokill):
    collision_list = []
    for group in grouplist:
        collided = pygame.sprite.spritecollide(sprite, group, dokill)
        for item in collided:
            collision_list.append(item)
    return collision_list


def get_monster_by_name(name, start_pos, player, bombs, soft_blocks, hard_blocks):
    monster = None
    if name == constants.Monster.BALLOM:
        monster = Ballom(start_pos, bombs, soft_blocks, hard_blocks)
    elif name == constants.Monster.ONIL:
        monster = Onil(start_pos, bombs, soft_blocks, hard_blocks)
    elif name == constants.Monster.DAHL:
        monster = Dahl(start_pos, bombs, soft_blocks, hard_blocks)
    elif name == constants.Monster.MINVO:
        monster = Minvo(start_pos, player, bombs, soft_blocks, hard_blocks)
    elif name == constants.Monster.DORIA:
        monster = Doria(start_pos, player, bombs, hard_blocks)
    elif name == constants.Monster.OVAPE:
        monster = Ovape(start_pos, bombs, hard_blocks)
    elif name == constants.Monster.TIGLON:
        monster = Tiglon(start_pos, player, bombs, soft_blocks, hard_blocks)
    # elif name == constants.Monster.PONTAN:
    if monster is None:
        raise ValueError
    return monster


class Blast(pygame.sprite.Sprite):
    def __init__(self, start_pos, type, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(0, 4 + type)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE
        self.frame = 0
        self.timer = constants.BLAST_TIME
        self.direction = direction
        self.type = type
        self.collide_rect_ratio = 0.1

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.kill()
        # Update image frame
        self.frame = (self.frame + constants.BLAST_ANIMATION_SPEED) % 7
        # Update image according to frame
        image_x, image_y = constants.BLAST_ANIMATION[self.type][int(self.frame)]
        self.image = pygame.transform.rotate(assets.Assets.get_image_at(image_x, image_y),
                                             (self.direction + 1) % 4 * 90)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, start_pos, blast_range, blasts, hard_blocks, soft_blocks, remote=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(0, 3)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE
        self.frame = 0
        self.timer = -1 if remote else constants.BOMB_TIME
        self.blasts = blasts
        self.blast_range = blast_range
        self.hard_blocks = hard_blocks
        self.soft_blocks = soft_blocks
        self.remote = remote

    def kill(self):
        if self.timer > 5 or self.timer < 0:
            self.timer = 5
        if self.timer == 0:
            self.blasts.add(Blast(self.get_tile_pos(), 2, 0))
            for direction in constants.Direction:
                for i in range(self.blast_range):
                    if i == 0:
                        continue
                    x, y = get_modified_position(self.get_tile_pos(), direction, i)
                    new_blast = Blast((x, y), 1, direction)
                    if pygame.sprite.spritecollide(new_blast, self.hard_blocks, False):
                        break
                    if pygame.sprite.spritecollide(new_blast, self.soft_blocks, True):
                        break
                    bombs = self.groups()[0]
                    pygame.sprite.spritecollide(new_blast, bombs, True)
                    self.blasts.add(new_blast)
                else:
                    x, y = get_modified_position(self.get_tile_pos(), direction, self.blast_range)
                    new_blast = Blast((x, y), 0, direction)
                    if pygame.sprite.spritecollide(new_blast, self.hard_blocks, False):
                        continue
                    if pygame.sprite.spritecollide(new_blast, self.soft_blocks, True):
                        continue
                    bombs = self.groups()[0]
                    pygame.sprite.spritecollide(new_blast, bombs, True)
                    self.blasts.add(new_blast)

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

    def get_tile_pos(self):
        return self.rect.center[0] // constants.SPRITE_SIZE, self.rect.center[1] // constants.SPRITE_SIZE


class Block(pygame.sprite.Sprite):
    def __init__(self, image_pos, start_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(image_pos[0], image_pos[1])
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE


class HardBlock(Block):
    def __init__(self, start_pos):
        super().__init__((3, 3), start_pos)


class SoftBlock(Block):
    def __init__(self, start_pos, bonus_type=-1, bonuses=None):
        super().__init__((4, 3), start_pos)
        self.frame = 0
        self.dead = 0
        self.bonus_type = bonus_type
        self.bonuses = bonuses

    def update(self):
        # TODO: DELETE 2 LINES BELOW
        # if self.bonus_type != -1:
        #     self.image = assets.Assets.get_image_at(self.bonus_type, 7)
        if self.dead:
            self.frame += constants.BLOCK_ANIMATION_SPEED
            if int(self.frame) == 6:
                if self.bonus_type != -1:
                    self.bonuses.add(Bonus((self.rect.x, self.rect.y), self.bonus_type))
                pygame.sprite.Sprite.kill(self)
                return
            image_x, image_y = constants.SOFT_BLOCK_DISAPPEARING_ANIMATION[int(self.frame)]
            self.image = assets.Assets.get_image_at(image_x, image_y)

    def kill(self):
        self.dead = 1


class Bonus(pygame.sprite.Sprite):
    def __init__(self, start_pos, bonus_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(bonus_type, 7)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]
        self.bonus_type = bonus_type


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
        self.__speed = constants.BASE_SPEED
        self.__max_bombs = 1
        self.__blast_range = 1
        self.speed_bonus = False
        self.detonator_bonus = False
        self.wall_walker_bonus = False
        self.bomb_walker_bonus = False
        self.fire_proof_bonus = False
        self.lives = 2
        self.dead = 0

    @property
    def speed(self):
        return self.__speed * 1.5 if self.speed_bonus else self.__speed

    @property
    def blast_range(self):
        return self.__blast_range

    @blast_range.setter
    def blast_range(self, blast_range):
        self.__blast_range = 5 if blast_range >= 5 else blast_range

    @property
    def max_bombs(self):
        return self.__max_bombs

    @max_bombs.setter
    def max_bombs(self, max_bombs):
        self.__max_bombs = 10 if max_bombs >= 10 else max_bombs

    def update(self):
        if self.dead:
            self.frame += constants.ANIMATION_SPEED
            if int(self.frame) == 7:
                self.lives -= 1
                return
            image_x, image_y = constants.BOMBERMAN_DEATH_ANIMATION[int(self.frame)]
            self.image = assets.Assets.get_image_at(image_x, image_y)
        else:
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

    def kill(self):
        if not self.dead:
            self.dead = 1
            self.frame = 0

    def get_tile_pos(self):
        return self.rect.center[0] // constants.SPRITE_SIZE, self.rect.center[1] // constants.SPRITE_SIZE


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.Assets.get_image_at(0, 0)
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0] * constants.SPRITE_SIZE
        self.rect.y = start_pos[1] * constants.SPRITE_SIZE
        self.direction = constants.Direction.RIGHT
        self.movement_animation = None
        self.death_animation = None
        self.obstacles = None
        self.frame = 0
        self.speed = 0
        self.dead = 0

    def update(self):
        if self.dead:
            self.die()
        else:
            self.animate()
            self.move()

    def move(self):
        raise NotImplemented

    def die(self):
        self.frame += constants.ANIMATION_SPEED
        if int(self.frame) == 4:
            pygame.sprite.Sprite.kill(self)
            return
        image_x, image_y = self.death_animation[int(self.frame)]
        self.image = assets.Assets.get_image_at(image_x, image_y)

    def animate(self):
        # Animate
        self.frame = (self.frame + constants.ANIMATION_SPEED) % 4
        image_x, image_y = self.movement_animation[self.direction // 2][int(self.frame)]
        self.image = assets.Assets.get_image_at(image_x, image_y)

    def get_tile_pos(self):
        return self.rect.center[0] // constants.SPRITE_SIZE, self.rect.center[1] // constants.SPRITE_SIZE

    def get_possible_directions(self):
        possible_directions = []
        for direction in constants.Direction:
            self.rect.x, self.rect.y = get_modified_position((self.rect.x, self.rect.y), direction, 1)
            if not spritegrouplistcollide(self, self.obstacles, False):
                possible_directions.append(direction)
            self.rect.x, self.rect.y = get_modified_position((self.rect.x, self.rect.y), direction, -1)
        return possible_directions

    def kill(self):
        self.frame = 0
        self.dead = 1


class AdvancedEnemy(Enemy):
    def __init__(self, start_pos, player):
        super().__init__(start_pos)
        self.dead = 0
        self.freeze = 0
        self.turn_ratio = 0
        self.freeze = 0
        self.turn_time = 0
        self.obstacles = None
        self.chase_radius = 0
        self.player = player
        self.random_turn_chance = 0.20

    def move(self):
        possible_directions = self.get_possible_directions()
        preferred_directions = self.get_preferred_directions()
        if len(possible_directions) > 0:
            if self.rect.x % constants.SPRITE_SIZE == 0 and self.rect.y % constants.SPRITE_SIZE == 0:
                if self.direction not in possible_directions:
                    for direction in preferred_directions:
                        if direction in possible_directions:
                            self.direction = direction
                            break
                    self.freeze = self.turn_time
                elif random.random() < self.turn_ratio:
                    for direction in preferred_directions:
                        if direction in possible_directions:
                            self.direction = direction
                            break
            if not self.freeze:
                self.rect.x, self.rect.y = get_modified_position((self.rect.x, self.rect.y),
                                                                 self.direction,
                                                                 self.speed)
            else:
                self.freeze -= 1

    def get_preferred_directions(self):
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        directions = [constants.Direction.LEFT, constants.Direction.DOWN,
                      constants.Direction.RIGHT, constants.Direction.UP]
        if math.sqrt(dx * dx + dy * dy) > self.chase_radius:
            return sorted(directions, key=lambda x: random.random())
        if random.random() < self.random_turn_chance:
            return sorted(directions, key=lambda x: random.random())
        rated_directions = [
            (constants.Direction.LEFT, dx),
            (constants.Direction.DOWN, -dy),
            (constants.Direction.RIGHT, -dx),
            (constants.Direction.UP, dy),
        ]
        rated_directions = sorted(rated_directions, key=lambda x: x[1])
        directions = []
        for direction, _ in rated_directions:
            directions.append(direction)
        return directions


class SimpleEnemy(Enemy):
    def __init__(self, start_pos):
        super().__init__(start_pos)
        self.dead = 0
        self.freeze = 0
        self.turn_ratio = 0
        self.freeze = 0
        self.turn_time = 0
        self.obstacles = None

    def move(self):
        possible_directions = self.get_possible_directions()
        if len(possible_directions) > 0:
            if self.rect.x % constants.SPRITE_SIZE == 0 and self.rect.y % constants.SPRITE_SIZE == 0:
                if self.direction not in possible_directions:
                    self.direction = sorted(possible_directions, key=lambda x: random.random())[0]
                    self.freeze = self.turn_time
                elif random.random() < self.turn_ratio:
                    self.direction = sorted(possible_directions, key=lambda x: random.random())[0]
            if not self.freeze:
                self.rect.x, self.rect.y = get_modified_position((self.rect.x, self.rect.y),
                                                                 self.direction,
                                                                 self.speed)
            else:
                self.freeze -= 1



class Ballom(SimpleEnemy):
    """The easiest enemy of them all. Slow and passive.

    Ballom has a very unpredictable movement pattern. They are slow and won't chase after
    Bomberman, but they turn or reverse direction upon colliding with a wall or bomb."""
    def __init__(self, start_pos, bombs, soft_blocks, hard_blocks):
        super().__init__(start_pos)
        self.speed = constants.BASE_SPEED * 0.5
        self.turn_ratio = 0.05
        self.turn_time = 15
        self.movement_animation = constants.BALLOOM_MOVEMENT_ANIMATION
        self.death_animation = constants.BALLOOM_DEATH_ANIMATION
        self.points = 100
        self.obstacles = [bombs, soft_blocks, hard_blocks]


class Onil(SimpleEnemy):
    """Medium-difficulty enemy. Quite quick, might chase after player.

    Onil moves quickly and randomly. They will move towards Bomberman when he is nearby. They
    are not likely to get stuck on walls and can be incredibly troublesome."""
    def __init__(self, start_pos, bombs, soft_blocks, hard_blocks):
        super().__init__(start_pos)
        self.speed = constants.BASE_SPEED
        self.turn_ratio = 0.15
        self.turn_time = 10
        self.movement_animation = constants.ONIL_MOVEMENT_ANIMATION
        self.death_animation = constants.ONIL_DEATH_ANIMATION
        self.points = 200
        self.obstacles = [bombs, soft_blocks, hard_blocks]


class Dahl(SimpleEnemy):
    """Very easy opponent. Slow and passive, prone to stucking into walls.

    It moves at slightly fast speed, doing some bouncy moves (it doesn't jump however). It is
    not hard to kill since they are not smart, even less intelligent than Balloms and won't
    try to chase Bomberman. They prefer to move from left to right, sometimes switching to up
    and down. Commonly get stuck in walls."""
    def __init__(self, start_pos, bombs, soft_blocks, hard_blocks):
        super().__init__(start_pos)
        self.speed = constants.BASE_SPEED
        self.turn_ratio = 0.10
        self.turn_time = 0
        self.movement_animation = constants.DAHL_MOVEMENT_ANIMATION
        self.death_animation = constants.DAHL_DEATH_ANIMATION
        self.points = 400
        self.obstacles = [bombs, soft_blocks, hard_blocks]


class Minvo(AdvancedEnemy):
    """Medium-difficulty enemy. Quick and chasing.

    They move as fast as Onils. Encountered after the Dahls. They will pursue Bomberman if he's
    nearby, but commonly get stuck if he's hiding."""
    def __init__(self, start_pos, player, bombs, soft_blocks, hard_blocks):
        super().__init__(start_pos, player)
        self.speed = constants.BASE_SPEED
        self.turn_ratio = 0.20
        self.turn_time = 0
        self.movement_animation = constants.MINVO_MOVEMENT_ANIMATION
        self.death_animation = constants.MINVO_DEATH_ANIMATION
        self.points = 800
        self.obstacles = [bombs, soft_blocks, hard_blocks]
        self.chase_radius = 6 * constants.SPRITE_SIZE
        self.random_turn_chance = 0.25


class Doria(AdvancedEnemy):
    """Difficult enemy. Quick, chasing, evading blocks and flying over Soft Blocks.

    It moves really slow, but it can move through Soft Blocks. It appears cyan-colored, just as
    the Onils are. Dorias are very smart, they will commonly attempt to chase Bomberman and they
    can evade bombs."""
    def __init__(self, start_pos, player, bombs, hard_blocks):
        super().__init__(start_pos, player)
        self.speed = constants.BASE_SPEED * 0.5
        self.turn_ratio = 0.50
        self.turn_time = 5
        self.movement_animation = constants.DORIA_MOVEMENT_ANIMATION
        self.death_animation = constants.DORIA_DEATH_ANIMATION
        self.points = 1000
        self.obstacles = [bombs, hard_blocks]
        self.chase_radius = 12 * constants.SPRITE_SIZE
        self.random_turn_chance = 0.30


class Ovape(SimpleEnemy):
    """Quite difficult enemy. They can fly over Soft Blocks.

    They resemble red, purple or pink ghosts that move through Soft Blocks. They are encountered
    after the Dorias They don't chase after Bomberman too commonly, unlike Dorias, but due to
    their wall-pass abilities, they can cause problems."""
    def __init__(self, start_pos, bombs, hard_blocks):
        super().__init__(start_pos)
        # TODO: implement fraction speeds - 0.75 for Ovape
        self.speed = constants.BASE_SPEED
        self.turn_ratio = 0.10
        self.turn_time = 5
        self.movement_animation = constants.OVAPE_MOVEMENT_ANIMATION
        self.death_animation = constants.OVAPE_DEATH_ANIMATION
        self.points = 2000
        self.obstacles = [bombs, hard_blocks]


class Tiglon(AdvancedEnemy):
    """Difficult enemy. Very fast, evading and chasing.

    Tiglon moves faster than most enemies, and is able to avoid bombs. It often pursues Bomberman.
    Their behavior and appearance is kind of similar to Minvos. Unlike Minvos, however, they're
    a bit faster and smarter. They're associated with the Fireproof Power-up and as such, will
    appear if said power up is blown up by a bomb, or the exit of a level with this power up
    present is bombed."""
    def __init__(self, start_pos, player, bombs, soft_blocks, hard_blocks):
        super().__init__(start_pos, player)
        self.speed = constants.BASE_SPEED
        self.turn_ratio = 0.35
        self.turn_time = 0
        self.movement_animation = constants.TIGLON_MOVEMENT_ANIMATION
        self.death_animation = constants.TIGLON_DEATH_ANIMATION
        self.points = 4000
        self.obstacles = [bombs, soft_blocks, hard_blocks]
        self.chase_radius = 12 * constants.SPRITE_SIZE
        self.random_turn_chance = 0.15


class Pontan(Enemy):
    """The most difficult enemy in the game. Fast, passing through Soft Blocks and chasing.

    Pontan moves very quickly, passing through Soft Blocks and constantly pursuing the player.
    They're associated with the Invincibility Power-up and as such, will appear if said power up
    is blown up by a bomb, or the exit of a level with this power up present is bombed or if the
    timer reaches zero. They are able to chase the player from one side of the screen to the other."""
    pass

