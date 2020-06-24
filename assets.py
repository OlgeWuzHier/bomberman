import pygame, constants


class Assets:
    @staticmethod
    def load():
        Assets.SPRITE_SHEET = pygame.image.load("sprite_sheet.png").convert()
        with open("gamemap.txt") as file:
            Assets.GAMEMAP = [line.rstrip('\n') for line in file]

    # loading images
    @staticmethod
    def get_image_at(x, y):
        """Returns image found in sprite sheet at given coordinates"""
        rectangle = pygame.Rect((
            x * (constants.SPRITE_SIZE),
            y * (constants.SPRITE_SIZE),
            constants.SPRITE_SIZE,
            constants.SPRITE_SIZE
        ))
        image = pygame.Surface(rectangle.size).convert()
        image.set_colorkey(constants.FIELD_COLOR)
        image.blit(Assets.SPRITE_SHEET, (0, 0), rectangle)
        return image

    @staticmethod
    def get_tiles():
        for y, line in enumerate(Assets.GAMEMAP):
            for x, cell in enumerate(line):
                yield x, y, cell
