import pygame as pg
import blitter as blt
import animator as an
from timer import *
from game_name.extra import *
from game_name.entities.stats import *
from game_name.game_map.map import *
from game_name.entities.combat import *
from json import load, dumps

class Entity():
# exceptions.
    class revivingNotDeadEntity(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
# ----------------- #

# loading from Json.
    def infoCode() -> str:
        return 'entity'

    @classmethod
    def saveEmptyDict(cls: 'Entity') -> dict:
        '''Saves an empty dict for the entity in the games_info json file.\n'''

        with open('infos/game.json', 'r') as file:
            entInfos = load(file)
 
            emptyEntDict: dict = {
                'x': 300,
                'y': 300,
            }

            with open('infos/game.json', 'r') as file: entInfos[cls.infoCode()] = emptyEntDict
            with open('infos/game.json', 'w') as file: file.write( dumps(entInfos, indent=2) )

    @classmethod
    def createInstanceWithDict(cls: 'Entity', entInfos: dict) -> 'Entity':
        '''Creates and returns instance of the entity based on the entity's info inside the dict.\n'''

        return cls.__init__( pg.math.Vector2(entInfos[cls.infoCode()]['x'], entInfos[cls.infoCode()]['y']) )

    @classmethod
    def handleJson(cls: 'Entity') -> None:
        '''Creates the player according to json data and returns it.\n'''

        with open('infos/game.json', 'r') as file:
            entInfos: dict = load(file)

            if cls.infoCode() not in entInfos.keys():
                Entity.player = cls(pg.math.Vector2(20,20))
                return
            
            cls.createInstanceWithDict(entInfos[cls.infoCode()])
# ---------------------------- #

    map: Map = 0

    dt = 0
    enemies: list['Entity'] = []
    player: 'Entity' = 0

    blitter: blt.Blitter = 0

    def __init__(self, pos: pg.math.Vector2, layer: int=0, speed_value: float=0, max_life: float=0, max_mana: float=0, max_stamina: float=0) -> None:
        self.pos: pg.math.Vector2 = pos
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2()
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()
        self.speed_value: float = speed_value

        self.layer: int = layer

        self.animator: an.Animator = an.Animator(pg.image.load('assets/entities/empty.png').convert_alpha(), [5,5], [1])
        self.blit_angle: float = 0

        #collision.
        self.rect: pg.rect.Rect = self.animator.image.get_rect().move(self.pos)
        self.damage_rect: pg.rect.Rect = self.rect
        self.mask = pg.mask.from_surface(self.animator.image)
        self.rect_adjust: tuple = (0,0)

        self.timers: list[Timer] = []
        self.attacks: list[Attack] = []
        self.current_attack: Attack = Attack()

        #booleans
        self.isLookingRight: bool = True

        self.alert_distance_squared: float = 0

        self.action: int = 0

        self.target: int = 0
        '''0-> no target.\n
           1-> targets enemies.\n
           2-> targets players.\n
           3-> targets enemies and players'''

        self.stats = Stats(max_life, max_mana, max_stamina)

        self.is_dead: bool = False
        self.active: bool = True
        self.stunned: bool = False

        self.distance_to_player_vec: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.distance_to_player_squared: float = 0

    def __str__(self) -> str:
        return Entity.infoCode()

    def center(self) -> pg.math.Vector2:
        '''Returns the center of the current sprite.\n'''
        return self.pos + pg.math.Vector2(self.animator.currentSpriteSize())*0.5

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

        if self.stats.is_taking_damage: speed = speed * 0.25

        speed = speed + self.speed_complement*Entity.dt

        return speed

    def isMoving(self) -> bool:
        '''Returns true if entity's speed is going to change it's position in the next loop movement.\n
           Considers movement lock variables in the moment of the call.\n'''
        return (self.getMovementSpeed() != pg.math.Vector2())

    def getLockMovement(self) -> bool:
        '''Returns true if entity's is allowed to move.\n'''
        return bool(self.action) or self.stunned

    def move(self) -> None:
        '''Moves the entity if movement isn't locked.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        if self.isGoingOutOfBounds(): self.fitInDisplayBounds()
        self.fitOutOfStructures()

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()
# ------------------- #

# blitting.
    def blit(self) -> None:
        '''Blits the instance's animator image using a blitter instance.\n'''

        if Entity.blitter == 0:
            return

        image = rotCenter(self.animator.image, self.blit_angle)
        Entity.blitter.addImage(self.layer, image, self.pos)

        self.blitStats()

    def blitStats(self) -> None:
        '''Abstract function to blit entity's stats.\n'''
# ----------------------- #

# interacting with game word.
    def resetAction(self) -> None:
        '''Resets entity action and current Attack.\n'''
        self.action = 0

    def resetAttack(self) -> None:
        '''Sets the current attack to be a empty attack.\n'''
        self.current_attack: Attack = Attack()

    def resetCombat(self) -> None:
        '''Resets the combat features of the entity.\n'''
        self.resetAction()
        self.resetAttack()

    def collidePlayer(self) -> None:
        '''Checks for collision with player and damages in.\n
           Rect and mask collision.\n'''
        if not self.damage_rect.colliderect(Entity.player.rect): return

        if self.mask.overlap(Entity.player.mask, Entity.player.pos-self.pos) != None:
            Entity.player.damageSelf(self.current_attack)
            Entity.player.complementSpeed(self.current_attack.knockback)

    def collideEnemies(self) -> None:
        '''Checks for collision with enemies and damages the collided ones.\n
           Rect collision.\n'''
        for en in Entity.enemies:
            if self.damage_rect.colliderect(en.rect):
                en.damageSelf(self.current_attack)

    def setHitbox(self) -> None:
        '''Entity's function for setting it's damage inflicter hitbox.\n
           Function has default call is the update procedure (inside collision update).\n'''
        self.damage_rect = self.rect.copy()

    def collisionUpdate(self) -> None:
        '''Updates the collision handle variables.\n
           The self.rect is a rect for checking general collision with the entity.\n
           While the self.damage_rect is a rect for checking damage infliction by the entity.\n'''
        image: pg.surface.Surface = rotCenter(self.animator.image, self.blit_angle)

        self.rect: pg.rect.Rect = image.get_rect().move(self.pos)
        self.rect = self.rect.inflate(self.rect_adjust[0],self.rect_adjust[1])
        self.setHitbox()

        self.mask: pg.mask.Mask = pg.mask.from_surface(image)

        if self.target in (1,3): self.collideEnemies()
        if self.target in (2,3): self.collidePlayer()
# ------------------------------ #

#
    def pull(self, target: pg.math.Vector2, speed_factor: float=1) -> None:
        '''Pulls the entity to the target.\n
           Sets the pulling action.\n'''
        self.action = -2
        distance_vec = target-self.center()
        distance = distance_vec.length()

        if distance <= 10: return

        self.complementSpeed( distance_vec * speed_factor / distance )

    def stopPull(self) -> None:
        '''Stops entity's pulling.\n'''
        self.resetAction()
#

# animation.
    def setLookingDir(self) -> bool:
        '''If self.speed_dir[0] is different than zero, changes the looking dir'''
        
        if self.speed_dir[0] > 0: self.isLookingRight = True
        elif self.speed_dir[0] < 0: self.isLookingRight = False
    
    def animationAction(self) -> None:
        '''Controls the entity's behavior based on the current action.\n'''
        if self.action == -1: self.animator.setEAP(lambda: self.die())
        if self.action == -2: self.animator.setEAP(lambda: self.resetAction())

    def controlAnimator(self) -> None:
        '''Flips the image based in the looking dir of the entitys.\n
           Proceed the animation update.\n'''
        self.animator.update(Entity.dt)

        self.setLookingDir()
        if not self.isLookingRight: self.animator.flipHorizontally()
# -------------------- #

# effects.
    def unstun(self) -> None:
        '''Un-stuns the entity.\n'''
        self.stunned = False

    def stun(self, effect: Stun) -> None:
        '''Stuns entity.\n'''
        if self.stunned: return

        self.resetCombat()

        self.stunned = True
        self.timers.append( Timer(effect.time, lambda: self.unstun(), 1) )
# ----------------------- #

# stats spend functions.
    def applyEffect(self, effect: Effect|None) -> None:
        '''Applies effect in instance.\n'''

        if isinstance(effect, Stun): self.stun(effect)

        return

    def damageSelf(self, attack: Attack) -> None:
        '''Procedure to damage entity.\n
           Applies the corresponding effect of the parameter to the entity.\n'''
        if not attack.instant: self.stats.spend(Entity.dt, attack.damage, 1)
        else: self.stats.spend(1, attack.damage, 1)

        self.applyEffect(attack.effect)

    def setCurrentAttack(self, attack: Attack) -> bool:
        '''Abstract for setting entities attack.\n
           If the attack can be used, sets it as current attack, applies it's cost and returns True.\n'''

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

        if not Entity.blitter.camera.getCaptureRect().contains(self.rect.move(self.getMovementSpeed())):
            return True
        return False

    def fitInDisplayBounds(self) -> None:
        '''Checks where entity has escaped from display, and fits it back.\n'''    
        fitVector = pg.math.Vector2(0,0)

        displayRect = Entity.blitter.camera.getCaptureRect()

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
        structs: list[Structure] = Entity.map.getStructuresInRectInLayer(self.layer, self.rect.copy(), pg.math.Vector2(64,64))

        for struct in structs:
            if not self.rect.colliderect(struct.rect): continue

            if self.mask.overlap_area(struct.mask, struct.getPos()-self.pos) == 0: continue

            distance = self.center()-struct.mask_centroid
            if distance != pg.math.Vector2(): distance = distance.normalize()*self.speed_value*1.5*Entity.dt

            self.pos = self.pos + distance
# ----------------------- #

# killing methods.
    def kill(self) -> None:
        '''Kills the entity after the current animation.\n
           At the end of the current animation the self.die() method will be called by default.\n'''
        self.action = -1
    
    def die(self) -> None:
        '''Instantly kills the entity.\n
           Makes the entity stop updating.\n'''
        self.is_dead = True
        self.resetCombat()
# ---------------------------- #

    def revive(self) -> None:
        '''Makes the entity update.\n
           If it was alredy alive, throws.\n'''
        if not self.is_dead: raise Entity.revivingNotDeadEntity 
        self.is_dead = False

    def __del__(self) -> None:
        '''Abstract function for saving entity's data before deleting.\n'''

# main procedures.
    def activate(self) -> None:
        '''Actives instance and activates it's timers.\n'''
        if not self.active: activateTimers(self.timers)
        self.active = True

    def deactivate(self) -> None:
        '''Deactives instance and deactivates it's timers.\n'''
        if self.active: deactivateTimers(self.timers)
        self.active = False

    def update(self) -> None:
        '''Does the loop procedures of a regular entity. Call loop reset at the end of the loop.\n'''
        if self.is_dead: return

        self.blit()

        if not self.active: return

        self.collisionUpdate()

        if not self.stats.update(Entity.dt): self.kill()
    
        self.controlAnimator()
        
        self.move()
        
        updateTimers(self.timers)

def blitMinimap(font: pg.font.Font) -> None:
    minimap = Entity.map.miniature.copy()
    scale_vec = Entity.map.scale_vec
    minimap_size = minimap.get_size()

    minimap.blit( pg.transform.scale_by(Entity.player.animator.image, 0.5),
                  (Entity.player.pos[0]*scale_vec[0], Entity.player.pos[1]*scale_vec[1]) )
    
    for en in Entity.enemies:
        minimap.blit( pg.transform.scale_by(en.animator.image, 0.5),
                      (en.pos[0]*scale_vec[0], en.pos[1]*scale_vec[1]) )

    Entity.blitter.addImage(Entity.blitter.lastLayer(),
                            minimap,
                            pg.math.Vector2(0,0))
    
    minimap_text = font.render('Minimap', 1, (0,0,0))

    Entity.blitter.addImage(Entity.blitter.lastLayer(),
                            minimap_text,
                            pg.math.Vector2( (minimap_size[0]-minimap_text.get_size()[0] )/2, 20))

def updateEnemies() -> None:
    '''Updates all the registered enemies.\n'''

    for en in Entity.enemies:
        en.update()

        if en.distance_to_player_squared <= en.alert_distance_squared: en.activate()
        elif en.distance_to_player_squared >= en.alert_distance_squared: en.deactivate()
