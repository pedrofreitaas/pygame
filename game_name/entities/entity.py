import pygame as pg
import blitter as blt
import animator as an
from timer import *

class Entity():

    dt = 0
    enemies: list['Entity'] = []
    player: 'Entity' = 0

    blitter: blt.Blitter = 0
    
    def __init__(self, pos: pg.math.Vector2, layer: int, speed_value: float) -> None:
        
        self.pos: pg.math.Vector2() = pos
        self.speed: pg.math.Vector2() = pg.math.Vector2()
        self.speed_value = speed_value

        self.layer = layer

        self.animator: an.Animator = an.Animator(pg.image.load('assets/entities/empty.png').convert_alpha(), [5,5], [1])
        self.blit_angle = 0
        self.rect = self.animator.image.get_rect().move(self.pos)
        self.mask = pg.mask.from_surface(self.animator.image)

        self.timers: list[Timer] = []

    def isMoving(self) -> bool:
        '''Return true if the entity is moving.\n'''
        return self.speed != pg.math.Vector2()

    def blit(self) -> None:
        '''Blits the instance's animator image using a blitter instance.\n'''

        if Entity.blitter == 0:
            return

        image = blt.rotCenter(self.animator.image, self.blit_angle)
        Entity.blitter.addImageInLayer(self.layer, image, self.pos)

    def move(self) -> None:
        '''Moves the entity.\n'''
        
        self.pos = self.pos + self.speed * Entity.dt
    
    def collisionUpdate(self) -> None:
        '''Updates the collision handle variables.\n'''
        
        image = blt.rotCenter(self.animator.image, self.blit_angle)

        self.rect = image.get_rect().move(self.pos)
        self.mask = pg.mask.from_surface(image)
    
    def controlAnimator(self) -> None:
        '''Controls what sprites will be animated based on the entity's behavior.\n'''
        pass

    def update(self) -> None:

        self.move()

        self.collisionUpdate()
        
        self.animator.update(Entity.dt)

        self.blit()

def updateEnemies() -> None:
    '''Updates all the registered enemies.\n'''

    for enemy in Entity.enemies:
        enemy.update()
