import enum

TICK_RATE = 60
TICK_TIME_MS = 1000 / TICK_RATE

BACKGROUND_COLOR = (200, 200, 200)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
FIELD_COLOR = (56, 135, 0)

SPRITE_SIZE = 32
WINDOW_WIDTH, WINDOW_HEIGHT = 16 * SPRITE_SIZE, 15 * SPRITE_SIZE
FIELD_WIDTH, FIELD_HEIGHT = 31 * SPRITE_SIZE, 13 * SPRITE_SIZE

BASE_SPEED = 2  # must be a divisor of SPRITE_SIZE
ANIMATION_SPEED = 0.1

BOMB_TIME = TICK_RATE * 2.5
BLAST_TIME = TICK_RATE * 0.5

# 7 frames in blast animation
BLAST_ANIMATION_SPEED = TICK_RATE / BLAST_TIME / 7
BLOCK_ANIMATION_SPEED = TICK_RATE / BLAST_TIME / 6
# ANIMATION SPRITE SHEET COORDINATES
# 1. CHARACTERS
# list[0] - going right or up, list[1] - going left or down
BALLOOM_MOVEMENT_ANIMATION = [
    [(3, 8), (4, 8), (5, 8), (4, 8)],
    [(0, 8), (1, 8), (2, 8), (1, 8)],
]
BALLOOM_DEATH_ANIMATION = [(7, 8), (8, 8), (9, 8), (10, 8), (11, 8)]

ONIL_MOVEMENT_ANIMATION = [
    [(3, 9), (4, 9), (5, 9), (4, 9)],
    [(0, 9), (1, 9), (2, 9), (1, 9)],
]
ONIL_DEATH_ANIMATION = [(7, 9), (8, 9), (9, 9), (10, 9), (11, 9)]

DAHL_MOVEMENT_ANIMATION = [
    [(3, 10), (4, 10), (5, 10), (4, 10)],
    [(0, 10), (1, 10), (2, 10), (1, 10)],
]
DAHL_DEATH_ANIMATION = [(7, 10), (8, 10), (9, 10), (10, 10), (11, 10)]

MINVO_MOVEMENT_ANIMATION = [
    [(3, 11), (4, 11), (5, 11), (4, 11)],
    [(0, 11), (1, 11), (2, 11), (1, 11)],
]
MINVO_DEATH_ANIMATION = [(7, 8), (8, 8), (9, 8), (10, 8), (11, 8)]

DORIA_MOVEMENT_ANIMATION = [
    [(3, 12), (4, 12), (5, 12), (4, 12)],
    [(0, 12), (1, 12), (2, 12), (1, 12)],
]
DORIA_DEATH_ANIMATION = [(7, 9), (8, 9), (9, 9), (10, 9), (11, 9)]

OVAPE_MOVEMENT_ANIMATION = [
    [(3, 13), (4, 13), (5, 13), (4, 13)],
    [(0, 13), (1, 13), (2, 13), (1, 13)],
]
OVAPE_DEATH_ANIMATION = [(7, 10), (8, 10), (9, 10), (10, 10), (11, 10)]

TIGLON_MOVEMENT_ANIMATION = [
    [(3, 14), (4, 14), (5, 14), (4, 14)],
    [(0, 14), (1, 14), (2, 14), (1, 14)],
]
TIGLON_DEATH_ANIMATION = [(7, 8), (8, 8), (9, 8), (10, 8), (11, 8)]

# Pontan is a spinning coin, so it has only one animation of movement
PONTAN_MOVEMENT_ANIMATION = [(0, 15), (1, 15), (2, 15), (3, 15)]
PONTAN_DEATH_ANIMATION = [(7, 8), (8, 8), (9, 8), (10, 8), (11, 8)]

# Bomberman movement - left, down, right, up
BOMBERMAN_MOVEMENT_ANIMATION = [
    [(0, 0), (1, 0), (2, 0), (1, 0)],
    [(3, 0), (4, 0), (5, 0), (4, 0)],
    [(0, 1), (1, 1), (2, 1), (1, 1)],
    [(3, 1), (4, 1), (5, 1), (4, 1)]
]
BOMBERMAN_DEATH_ANIMATION = [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]

# 2. ITEMS
BOMB_TICKING_ANIMATION = [(0, 3), (1, 3), (2, 3), (1, 3)]

# [0 - ending, 1 - mid, 2 - center]
BLAST_ANIMATION = [
    [(0, 4), (1, 4), (2, 4), (3, 4), (2, 4), (1, 4), (0, 4)],
    [(0, 5), (1, 5), (2, 5), (3, 5), (2, 5), (1, 5), (0, 5)],
    [(0, 6), (1, 6), (2, 6), (3, 6), (2, 6), (1, 6), (0, 6)],
]

SOFT_BLOCK_DISAPPEARING_ANIMATION = [(5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]


class Direction(enum.IntEnum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3


class Bonus(enum.IntEnum):
    EXTRA_BOMB = 0  # 10 at max
    FIRE_RANGE = 1  # 5 at max
    SPEEDUP = 2  # Bomberman's speed is doubled
    WALL_WALKER = 3  # Walk through Soft Blocks, lost after death
    DETONATOR = 4  # Space to set the bomb(s), Enter to detonate it(/them), lost after death
    BOMB_WALKER = 5  # Walk through your bombs, lost after death
    FLAME_PROOF = 6  # Immune to your own bombs, lasts forever, lost after death
    MYSTERY = 7  # Invisible for bombs and enemies, lasts 35 seconds


class Monster(enum.IntEnum):
    BALLOM = 0,
    ONIL = 1,
    DAHL = 2,
    MINVO = 3,
    DORIA = 4,
    OVAPE = 5,
    TIGLON = 6,
    PONTAN = 7


# Ballons, Onils, Dahls, Minvos, Dorias, Ovapes, Tiglons, Pontans, Bonus_number
LEVEL_CONTENT_LIST = [
    ([6, 0, 0, 0, 0, 0, 0, 0], 1),  # 1
    ([3, 3, 0, 0, 0, 0, 0, 0], 0),  # 2
    ([2, 2, 2, 0, 0, 0, 0, 0], 4),  # 3
    ([1, 1, 2, 2, 0, 0, 0, 0], 2),  # 4
    ([0, 4, 3, 0, 0, 0, 0, 0], 0),  # 5

    ([0, 2, 3, 2, 0, 0, 0, 0], 0),  # 6
    ([0, 2, 3, 0, 2, 0, 0, 0], 1),  # 7
    ([0, 1, 2, 4, 0, 0, 0, 0], 4),  # 8
    ([0, 1, 1, 4, 0, 1, 0, 0], 5),  # 9
    ([0, 1, 1, 1, 1, 3, 0, 0], 3),  # 10

    ([0, 1, 2, 3, 1, 1, 0, 0], 0),  # 11
    ([0, 1, 1, 1, 1, 4, 0, 0], 0),  # 12
    ([0, 0, 3, 3, 0, 2, 0, 0], 4),  # 13
    ([0, 0, 0, 0, 7, 0, 1, 0], 5),  # 14
    ([0, 0, 1, 3, 0, 3, 1, 0], 1),  # 15

    ([0, 0, 0, 3, 0, 4, 1, 0], 3),  # 16
    ([0, 0, 5, 0, 0, 2, 1, 0], 0),  # 17
    ([3, 3, 0, 0, 0, 0, 2, 0], 5),  # 18
    ([1, 1, 3, 0, 1, 0, 2, 0], 0),  # 19
    ([0, 1, 1, 1, 1, 2, 2, 0], 4),  # 20

    ([0, 0, 0, 0, 3, 4, 2, 0], 5),  # 21
    ([0, 0, 4, 3, 0, 1, 1, 0], 4),  # 22
    ([0, 0, 2, 2, 2, 2, 1, 0], 0),  # 23
    ([0, 0, 1, 1, 2, 4, 1, 0], 4),  # 24
    ([0, 2, 1, 1, 2, 2, 1, 0], 5),  # 25

    ([1, 1, 1, 1, 1, 2, 1, 0], 7),  # 26
    ([1, 1, 0, 0, 1, 5, 1, 0], 1),  # 27
    ([0, 1, 3, 3, 0, 1, 1, 0], 0),  # 28
    ([0, 0, 0, 0, 5, 2, 2, 0], 4),  # 29
    ([0, 0, 3, 2, 2, 1, 1, 0], 6),  # 30

    ([0, 2, 2, 2, 2, 2, 0, 0], 3),  # 31
    ([0, 1, 1, 3, 0, 4, 1, 0], 0),  # 32
    ([0, 0, 2, 2, 1, 3, 2, 0], 4),  # 33
    ([0, 0, 2, 3, 0, 3, 2, 0], 7),  # 34
    ([0, 0, 2, 1, 1, 3, 2, 0], 5),  # 35

    ([0, 0, 2, 2, 0, 3, 3, 0], 7),  # 36
    ([0, 0, 2, 1, 1, 3, 3, 0], 4),  # 37
    ([0, 0, 2, 2, 0, 3, 3, 0], 3),  # 38
    ([0, 0, 1, 1, 2, 2, 4, 0], 5),  # 39

    ([0, 0, 1, 2, 0, 3, 4, 0], 7),  # 40
    ([0, 0, 1, 1, 1, 3, 4, 0], 4),  # 41
    ([0, 0, 0, 1, 1, 3, 5, 0], 3),  # 42
    ([0, 0, 0, 1, 1, 2, 6, 0], 5),  # 43
    ([0, 0, 0, 1, 1, 2, 6, 0], 4),  # 44

    ([0, 0, 0, 0, 2, 2, 6, 0], 7),  # 45
    ([0, 0, 0, 0, 2, 2, 6, 0], 3),  # 46
    ([0, 0, 0, 0, 2, 2, 6, 0], 5),  # 47
    ([0, 0, 0, 0, 1, 2, 6, 1], 4),  # 48
    ([0, 0, 0, 0, 2, 1, 6, 1], 6),  # 49
    ([0, 0, 0, 0, 2, 1, 5, 2], 7)  # 50
]
