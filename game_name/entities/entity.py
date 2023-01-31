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

        #booleans
        self.isLookingRight: bool = True
        self.blockMove_H: bool = False
        self.blockMove_V: bool = False

        self.action: int = 0

    def isMoving(self) -> bool:
        '''Return true if the entity is moving.\n'''
        return self.speed != pg.math.Vector2()

    def blit(self) -> None:
        '''Blits the instance's animator image using a blitter instance.\n'''

        if Entity.blitter == 0:
            return

        image = blt.rotCenter(self.animator.image, self.blit_angle)
        Entity.blitter.addImageInLayer(self.layer, image, self.pos)

    def setLockMovement(self, value: bool, flag: int=0) -> None:
        '''Flag = 0 -> sets horizontal and vertical movement block with value.\n
           Flag = 1 -> sets horizontal movement block with value.\n
           Flag = 2 -> sets vertical movement block with value.\n'''
        if type(value) != type(True):
            raise ValueError
        
        if flag in [0,1]:
            self.blockMove_H = value
        if flag in [0,2]:
            self.blockMove_V = value

    def move(self) -> None:
        '''Moves the entity if movement isn't locked.\n'''
        
        speed = self.speed * Entity.dt

        if not self.blockMove_H:
            self.pos[0] = self.pos[0] + speed[0]
        if not self.blockMove_V:
            self.pos[1] = self.pos[1] + speed[1]
    
    def center(self) -> pg.math.Vector2:
        '''Returns the center of the current sprite.\n'''
        return self.pos + pg.math.Vector2(self.animator.currentSpriteSize())*0.5

    def collisionUpdate(self) -> None:
        '''Updates the collision handle variables.\n'''
        
        image = blt.rotCenter(self.animator.image, self.blit_angle)

        self.rect = image.get_rect().move(self.pos)
        self.mask = pg.mask.from_surface(image)
    
    def setLookingDir(self) -> bool:
        '''If self.speed[0] is different than zero, changes the looking dir'''
        
        if self.speed[0] > 0: self.isLookingRight = True
        elif self.speed[0] < 0: self.isLookingRight = False

    def controlAnimator(self) -> None:
        '''Flips the image based in the looking dir of the entitys.\n'''

        self.setLookingDir()
        if not self.isLookingRight: self.animator.flipHorizontally()

    def loopReset(self) -> None:
        '''Reset's variables of the instance for a new loop.\n'''
        self.blockMove_H = False
        self.blockMove_V = False

    def resetAction(self) -> None:
        '''Resets entity combat action.\n'''
        self.action = 0

    def attack(self) -> None:
        '''Toogles player's attack, if possible.\n'''
        if self.action == 0:
            self.action = 1

    def defend(self) -> None:
        '''Toggles player's defense, if possible.\n'''
        if self.action == 0:
            self.action = 2

    def cast(self) -> None:
        '''Toggles player's casting, if possible.\n'''
        if self.action == 0:
            self.action = 3

    def update(self) -> None:
        '''Does the loop procedures of a regular entity. Call loop reset at the end of the loop.\n'''

        self.collisionUpdate()
        
        self.controlAnimator()
        self.animator.update(Entity.dt)
        
        self.move()

        self.blit()
        
        self.loopReset()

def updateEnemies() -> None:
    '''Updates all the registered enemies.\n'''

    for enemy in Entity.enemies:
        enemy.update()
