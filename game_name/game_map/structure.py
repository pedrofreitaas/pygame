import pygame as pg

class Structure():

    def __init__(self, grid: pg.math.Vector2, image: pg.surface.Surface, props: dict) -> None:
        self.grid: tuple[int,int] = grid
        self.image: pg.surface.Surface = image

        delta_pos = pg.math.Vector2()
        width = 32
        height = 32

        if type(props) == type(dict()):
            width = props['w']
            height = props['h']
            delta_pos = pg.math.Vector2(props['delta_x'], props['delta_y'])

        self.rect = pg.rect.Rect(self.getPos()+delta_pos, (width, height) )

    def getPos(self) -> pg.math.Vector2:
        return self.grid * 32