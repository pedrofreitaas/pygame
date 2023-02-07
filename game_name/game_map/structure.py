import pygame as pg

class Structure():
    def __init__(self, grid: pg.math.Vector2, image: pg.surface.Surface) -> None:
        self.grid = grid
        self.image = image

    def getPos(self) -> pg.math.Vector2:
        return self.grid * 32

    def getRect(self) -> pg.rect.Rect:
        return self.image.get_rect().move(self.getPos())