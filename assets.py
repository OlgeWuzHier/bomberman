import constants
import pygame


class Assets:
    @staticmethod
    def load():
        """Loads sprite sheet, basic game map (location of player, hardblocks
        and places with disabled soft-block and monsters spawning) and main font."""
        Assets.SPRITE_SHEET = pygame.image.load("sprite_sheet.png").convert()
        with open("gamemap.txt") as file:
            Assets.GAMEMAP = [line.rstrip('\n') for line in file]
        Assets.FONT = pygame.font.Font("PressStart2P-Regular.ttf", 16)

    # loading images
    @staticmethod
    def get_image_at(x, y):
        """Returns image found in sprite sheet at given coordinates."""
        rectangle = pygame.Rect((
            x * constants.SPRITE_SIZE,
            y * constants.SPRITE_SIZE,
            constants.SPRITE_SIZE,
            constants.SPRITE_SIZE
        ))
        image = pygame.Surface(rectangle.size).convert()
        image.set_colorkey(constants.FIELD_COLOR)
        image.blit(Assets.SPRITE_SHEET, (0, 0), rectangle)
        return image

    @staticmethod
    def get_tiles():
        """Yields gamemap's cells one by one in format (x, y, content). X and Y are coordinates,
        content is a character (or space) that was in the gamemap file in that place."""
        for y, line in enumerate(Assets.GAMEMAP):
            for x, cell in enumerate(line):
                yield x, y, cell

    @staticmethod
    def get_font():
        return Assets.FONT
