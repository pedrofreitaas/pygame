from pytmx import TiledObject
import blitter as blt
from pygame.math import *
from pygame.surface import Surface
from pygame.mask import from_surface, Mask

class Object():
    '''Similar to structure but can move.\n'''
    all_objects: list['Object'] = []
    dt: float = 0

    def __init__(self, obj: TiledObject) -> None:
        self.pos: Vector2 = Vector2(obj.x, obj.y)
        self.image: Surface = obj.image.convert_alpha()
        self.mask: Mask = from_surface(self.image)

        self.speed_dir: Vector2 = Vector2(0,0)
        self.speed_value: float = 60

    def setSpeedDir(self, vec: Vector2) -> None:
        self.speed_dir = vec

    def getMovementSpeed(self) -> Vector2:
        return self.speed_value * self.speed_dir * Object.dt

    def move(self) -> None:
        self.pos += self.getMovementSpeed()

    def blit(self, blitter: blt.Blitter) -> None:
        blitter.addImage(0, self.image, self.pos)

    def __del__(self) -> None:
        Object.all_objects.remove(self)

    def update(self) -> None:
        self.move()

def updateObjs(dt: float, objs: list[Object]=Object.all_objects) -> None:
    Object.dt = dt
    for obj in objs: obj.update()
