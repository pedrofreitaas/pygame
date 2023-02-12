import pygame as pg
import blitter as blt
import animator as an
from timer import *
from game_name.extra import *
from game_name.entities.stats import *
from game_name.game_map.map import *

class Entity():
    map: Map = 0

    dt = 0
    enemies: list['Entity'] = []
    player: 'Entity' = 0

    blitter: blt.Blitter = 0

    blit_id: int = -1

    def generateBlitID(self) -> int:
        '''Generates a unique blit_ID for entities, that is negative to prevent conflicts with tiles IDs.\n'''
        id = Entity.blit_id
        Entity.blit_id -= 1
        return id
    
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

        self.is_dead = False

        self.blit_id = 0

# movement.
    def complementSpeed(self, complement: pg.math.Vector2) -> None:
        '''Complement parameter is going to sum in entity's movement.\n
           This isn't affected by movement lock.\n
           This isnt't affect by entity's speed value, only by delta time.\n
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

        if self.stats.is_taking_damage: speed = speed * 0.4

        speed = speed + self.speed_complement*Entity.dt

        return speed

    def isMoving(self) -> bool:
        '''Returns true if entity's speed is going to change it's position in the next loop movement.\n
           Considers movement lock variables in the moment of the call.\n'''
        return (self.getMovementSpeed() != pg.math.Vector2())

    def getLockMovement(self) -> bool:
        '''Returns a tuple that checks entity's current action adn returns if it's moving or not.\n'''
        return bool(self.action)

    def move(self) -> None:
        '''Moves the entity if movement isn't locked.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        if self.isGoingOutOfBounds(): self.fitInDisplayBounds()
        self.fitOutOfStructures()

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()
# ------------------- #

    def blit(self) -> None:
        '''Blits the instance's animator image using a blitter instance.\n'''

        if Entity.blitter == 0:
            return

        image = rotCenter(self.animator.image, self.blit_angle)
        Entity.blitter.addImageInLayer(self.layer, image, self.pos, self.blit_id)

        self.blitStats()

    def blitStats(self) -> None:
        '''Abstract function to blit entity's stats.\n'''

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

        if self.action == -1:
            self.animator.setEAP(lambda: self.die())

    def controlAnimator(self) -> None:
        '''Flips the image based in the looking dir of the entitys.\n'''

        self.setLookingDir()
        if not self.isLookingRight: self.animator.flipHorizontally()

    def resetAction(self) -> None:
        '''Resets entity action.\n'''
        self.action = 0

# stats spend functions.
    def damageSelf(self, value: float, instant=False) -> None:
        '''Procedure to damage entity.\n
           Instant flag true, to be used if the damage will be done in one single call.\n
           Instant flag false, to be used if the damage will tick many times.\n'''
        if not instant: self.stats.spend(Entity.dt, value, 1)
        else: self.stats.spend(1, value, 1)

    def useMana(self, value: float, instant=False) -> None:
        '''Procedure to use entity's Mana.\n
           Instant flag true, to be used if the damage will be done in one single call.\n
           Instant flag false, to be used if the damage will tick many times.\n'''
        if not instant: self.stats.spend(Entity.dt, value, 2)
        else: self.stats.spend(1, value, 2)

    def useStamina(self, value: float, instant=False) -> None:
        '''Procedure to use entity's stamina.\n
           Instant flag true, to be used if the damage will be done in one single call.\n
           Instant flag false, to be used if the damage will tick many times.\n'''
        if not instant: self.stats.spend(Entity.dt, value, 3)
        else: self.stats.spend(1, value, 3)
# ---------------------- #

# Movement collision.
    def isGoingOutOfBounds(self) -> bool:
        '''Returns true if the entity is going out of display, according\n
           to entity's speed and current state of movement locking.\n'''
        
        displayRect = Entity.blitter.camera.captureRect()

        if not displayRect.contains(self.rect.move(self.getMovementSpeed())):
            return True
        return False

    def fitInDisplayBounds(self) -> None:
        '''Checks where entity has escaped from display, and fits it back.\n'''
        fitVector = pg.math.Vector2(0,0)

        displayRect = Entity.blitter.camera.captureRect()

        top_escape = self.rect.top - displayRect.top
        if top_escape < 0: fitVector[1] = fitVector[1]-top_escape

        bottom_escape = self.rect.bottom - displayRect.bottom
        if bottom_escape > 0: fitVector[1] = fitVector[1]-bottom_escape

        left_escape = self.rect.left - displayRect.left
        if left_escape < 0: fitVector[0] = fitVector[0]-left_escape

        right_escape = self.rect.right - displayRect.right
        if right_escape > 0: fitVector[0] = fitVector[0]-right_escape
            
        self.pos = self.pos + fitVector

    def fitOutOfStructures(self) -> None:
        '''Makes sures the entity is out of structures.\n'''
        structs: list[Structure] = Entity.map.getStructuresInRectInLayer(self.layer, self.rect.copy())

        for struct in structs:
            if not self.rect.colliderect(struct.rect): continue

            if self.mask.overlap_area(struct.mask, struct.getPos()-self.pos) == 0: continue

            distance = self.center()-pg.math.Vector2(struct.rect.center)
            if distance != pg.math.Vector2(): distance = distance.normalize()*self.speed_value*Entity.dt

            self.pos = self.pos + distance
# ----------------------- #

    def kill(self) -> None:
        '''Sets the entity death animation.\n'''
        self.action = -1
    
    def die(self) -> None:
        '''Makes the entity stop updating.\n'''
        self.is_dead = True

    def update(self) -> None:
        '''Does the loop procedures of a regular entity. Call loop reset at the end of the loop.\n'''
        if self.is_dead: return

        self.collisionUpdate()

        if not self.stats.update(Entity.dt): self.kill()
        
        self.animator.update(Entity.dt)
        self.controlAnimator()
        
        self.move()

        self.blit()
        
        updateTimers(self.timers)

def updateEnemies() -> None:
    '''Updates all the registered enemies.\n'''

    for enemy in Entity.enemies:
        enemy.update()
