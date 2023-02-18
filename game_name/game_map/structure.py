import pygame as pg

class Structure():
    def __init__(self, grid: pg.math.Vector2, image: pg.surface.Surface, id: int) -> None:
        self.image: pg.surface.Surface = image
        self.mask: pg.mask.Mask = pg.mask.from_surface(self.image)
        self.id: int = id

        self.rect = pg.rect.Rect( grid*32, (32, 32) )
        
        self.mask_centroid: pg.math.Vector2 = self.getPos()+pg.math.Vector2(self.mask.centroid())

    def getPos(self) -> pg.math.Vector2:
        return pg.math.Vector2(self.rect.topleft)

    def getGrid(self) -> pg.math.Vector2:
        return pg.math.Vector2(self.rect.topleft)/32