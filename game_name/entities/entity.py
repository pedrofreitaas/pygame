import pygame as pg
import blitter as blt
import animator as an
from timer import *
from game_name.extra import *
from game_name.entities.stats import *

class Entity():

    dt = 0
    enemies: list['Entity'] = []
    player: 'Entity' = 0

    blitter: blt.Blitter = 0
    display_rect: pg.rect.Rect = pg.display.get_surface().get_rect()
    
    def __init__(self, pos: pg.math.Vector2, layer: int, speed_value: float, max_life: float, max_mana: float, max_stamina: float) -> None:
        
        self.pos: pg.math.Vector2 = pos
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2()
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()
        self.speed_value: float = speed_value

        self.layer: int = layer

        self.animator: an.Animator = an.Animator(pg.image.load('assets/entities/empty.png').convert_alpha(), [5,5], [1])
        self.blit_angle: float = 0
        self.rect = self.animator.image.get_rect().move(self.pos)
        self.mask = pg.mask.from_surface(self.animator.image)
        self.rect_adjust: tuple = [0,0]

        self.timers: list[Timer] = []

        #booleans
        self.isLookingRight: bool = True

        self.action: int = 0

        self.stats = Stats(max_life, max_mana, max_stamina)

    def complementSpeed(self, complement: pg.math.Vector2) -> None:
        '''Complement parameter is going to sum in entity's movement.\n
           This isn't affected by loop's delta time.\n
           This isn't affected by movement lock.\n
           Complemented speeds can still be complemented.\n'''
        self.speed_complement = self.speed_complement + complement

    def tryingToMove(self) -> bool:
        '''Returns true is speed is different than 0 vector.\n'''
        return self.speed_dir != pg.math.Vector2()

    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Returns the speed the entity will move in the next loop conclusion.\n
           Considering movement locks at the moment of the call.\n
           Considering the speed_complement value of the loop.\n'''

        speed = pg.math.Vector2()

        if self.speed_dir == pg.math.Vector2(): speed = self.speed_dir
        else: speed = self.speed_dir.normalize() * Entity.dt * self.speed_value

        if self.getLockMovement(): speed = pg.math.Vector2()

        speed = speed + self.speed_complement

        return speed

    def isMoving(self) -> bool:
        '''Returns true if entity's speed is going to change it's position in the next loop movement.\n
           Considers movement lock variables in the moment of the call.\n'''
        return (self.getMovementSpeed() != pg.math.Vector2())

    def blit(self) -> None:
        '''Blits the instance's animator image using a blitter instance.\n'''

        if Entity.blitter == 0:
            return

        image = rotCenter(self.animator.image, self.blit_angle)
        Entity.blitter.addImageInLayer(self.layer, image, self.pos)

        self.blitStats()

    def blitStats(self) -> None:
        '''Abstract function to blit entity's stats.\n'''

    def getLockMovement(self) -> bool:
        '''Returns a tuple that checks entity's current action adn returns if it's moving or not.\n'''
        return bool(self.action)

    def move(self) -> None:
        '''Moves the entity if movement isn't locked.\n'''
        if self.isGoingOutOfBounds(): self.fitInDisplayBounds()

        speed = self.getMovementSpeed()

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()

        self.pos = self.pos + speed
    
    def center(self) -> pg.math.Vector2:
        '''Returns the center of the current sprite.\n'''
        return self.pos + pg.math.Vector2(self.animator.currentSpriteSize())*0.5

    def collisionUpdate(self) -> None:
        '''Updates the collision handle variables.\n'''
        
        image: pg.surface.Surface = rotCenter(self.animator.image, self.blit_angle)

        self.rect: pg.rect.Rect = image.get_rect().move(self.pos)
        self.rect = self.rect.inflate(self.rect_adjust[0],self.rect_adjust[1])

        self.mask: pg.mask.Mask = pg.mask.from_surface(image)
    
    def setLookingDir(self) -> bool:
        '''If self.speed_dir[0] is different than zero, changes the looking dir'''
        
        if self.speed_dir[0] > 0: self.isLookingRight = True
        elif self.speed_dir[0] < 0: self.isLookingRight = False
    
    def animationAction(self) -> None:
        '''Controls the entity's behavior based on the current action.\n'''

    def controlAnimator(self) -> None:
        '''Flips the image based in the looking dir of the entitys.\n'''

        self.setLookingDir()
        if not self.isLookingRight: self.animator.flipHorizontally()

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

    def damageSelf(self, value: float) -> None:
        '''Procedure to damage entity.\n'''
        self.stats.spend(Entity.dt, value, 1)

    def isGoingOutOfBounds(self) -> bool:
        '''Returns true if the entity is going out of display, according\n
           to entity's speed and current state of movement locking.\n'''
        
        if not Entity.display_rect.contains(self.rect.move(self.getMovementSpeed())):
            return True
        return False

    def fitInDisplayBounds(self) -> None:
        '''Checks where entity has escaped from display, and fits it back.\n'''
        fitVector = pg.math.Vector2(0,0)

        top_escape = self.rect.top - Entity.display_rect.top
        if top_escape < 0: fitVector[1] = fitVector[1]-top_escape

        bottom_escape = self.rect.bottom - Entity.display_rect.bottom
        if bottom_escape > 0: fitVector[1] = fitVector[1]-bottom_escape

        left_escape = self.rect.left - Entity.display_rect.left
        if left_escape < 0: fitVector[0] = fitVector[0]-left_escape

        right_escape = self.rect.right - Entity.display_rect.right
        if right_escape > 0: fitVector[0] = fitVector[0]-right_escape
            
        self.complementSpeed(fitVector)

    def update(self) -> None:
        '''Does the loop procedures of a regular entity. Call loop reset at the end of the loop.\n'''

        self.collisionUpdate()
        self.stats.update(Entity.dt)
        
        self.animator.update(Entity.dt)
        self.controlAnimator()
        
        self.move()

        self.blit()
        
        updateTimers(self.timers)

def updateEnemies() -> None:
    '''Updates all the registered enemies.\n'''

    for enemy in Entity.enemies:
        enemy.update()
