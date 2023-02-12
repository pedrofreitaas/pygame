import pygame as pg

class Structure():

    def __init__(self, grid: pg.math.Vector2, image: pg.surface.Surface) -> None:
        self.image: pg.surface.Surface = image
        self.mask: pg.mask.Mask = pg.mask.from_surface(self.image)

        self.rect = pg.rect.Rect( grid*32, (32, 32) )

    def getPos(self) -> pg.math.Vector2:
        return pg.math.Vector2(self.rect.topleft)

    def getGrid(self) -> pg.math.Vector2:
        return pg.math.Vector2(self.rect.topleft)/32