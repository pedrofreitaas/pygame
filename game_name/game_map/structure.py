import pygame as pg

class Structure():

    def __init__(self, grid: pg.math.Vector2, image: pg.surface.Surface, props: dict) -> None:
        self.image: pg.surface.Surface = image
        self.mask: pg.mask.Mask = pg.mask.from_surface(self.image)

        self.hasExclusiveHitbox = False

        delta_pos = pg.math.Vector2()
        width = 32
        height = 32

        if type(props) == type(dict()):
            self.hasExclusiveHitbox = True

            width = props['w']
            height = props['h']
            delta_pos = pg.math.Vector2(props['delta_x'], props['delta_y'])

        self.rect = pg.rect.Rect( (grid*32) +delta_pos, (width, height) )

    def getPos(self) -> pg.math.Vector2:
        return pg.math.Vector2(self.rect.topleft)