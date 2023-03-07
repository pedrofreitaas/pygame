from game_name.entities.power import *
from game_name.game_map.structure import *

spritesheet = ['assets/entities/player/powers/hookax.png',
               'assets/entities/player/powers/chain_link.png']

class Hookax(Power):
    chain_link: pg.surface.Surface = pg.image.load(spritesheet[1]).convert_alpha()
    
    def __init__(self) -> None:
        super().__init__(layer=1, speed_value=250, caster_stats=Entity.player.stats, damage=1, mana_cost=15, stamina_cost=0, range=0, instant=False, cooldown=3, effect=None)

        self.animator = an.Animator( pg.image.load(spritesheet[0]).convert_alpha(),
                                     (80,80),
                                     (1,5) )
        
        self.hit_pos: pg.math.Vector2 = self.pos

        self.pull_cost: float = 6.4
        self.push_cost: float = 8.7
        
        self.animator.resizeSprites( (40,40) )

        self.pulling: bool = False
        self.pushing: bool = False

        self.hitted_entity: Entity|None = None
        self.vec: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.target: int = 3
        
        self.active_time: float = 12
        self.timers.append( Timer(self.active_time, lambda: self.kill(), -1) )

        self.rope_length: float = 450
        self.traveled_distance_squared: float = 0

        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.hookax'
        
    def use(self) -> bool:
        if not super().use(): return

        self.hitted_entity = None
        self.pulling = False
        self.pushing = False

        self.traveled_distance_squared: float = 0

        self.pos = Entity.player.center()- (pg.math.Vector2( self.animator.currentSpriteSize() )/2)
        self.hit_pos = pg.mouse.get_pos()- Entity.blitter.camera.getPos()
        self.speed_dir = (self.hit_pos-self.pos).normalize()

#
    def collidePlayer(self) -> None:
        '''Catches the hookax back if the player is next to it, recovering player's mana.\n'''
        if not (self.pulling or self.pushing): return
        if (self.center()-Entity.player.center()).length_squared() > 400: return

        self.stats.add(1, 10, 2)
        self.deactivate()

    def collideEnemies(self) -> None:
        '''If hookax hasn't collided yet and is moving, verifies enemy collision and sticks the hookax to the hitted enemy.\n'''
        if self.hitted_entity != None: return

        for en in Entity.enemies:
            if self.damage_rect.colliderect(en.rect):

                if self.mask.overlap_area(en.mask, en.pos-self.pos) <= 0: continue

                self.hitted_entity = en
                self.vec = self.center()-en.center()
                
                break

    def collideStructs(self) -> None:
        '''If hookax hasn't collided yet and it's moving, verifies collision with structures.\n
           If collided, stops the instance.\n'''
        if self.hitted_entity != None: return
        if not Entity.map.structExists(self.rect, 1): return

        self.speed_dir = pg.math.Vector2(0,0)
    
    def collisionUpdate(self) -> None:
        super().collisionUpdate()
        self.collideStructs()
#

#
    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == -1:
            self.animator.setRange( (1,5) )
            return

        self.animator.setRange((0,1))
#

#
    def move(self) -> None:
        '''Moves the hookax in the fire direction.\n
           If it has hitted entity, always drags the hookax to be at the hit_distance from entity.\n'''
        if self.traveled_distance_squared >= self.rope_length and not self.pulling: return
        
        if self.hitted_entity != None: 
            self.pos = self.hitted_entity.center()-self.vec
            return

        self.traveled_distance_squared += self.getMovementSpeed().length_squared()

        return super().move()
    
    def pull(self) -> None:
        '''Pulls the hookax and what is sticked to it in the player's direction.\n
           Spends player mana.\n'''
        if not self.pulling: return
        if not self.stats.spend(Entity.dt, self.pull_cost, 2): return

        if self.hitted_entity != None: self.hitted_entity.pull(Entity.player.center(), self.speed_value)
        else: super().pull(Entity.player.center(), self.speed_value)

    def push(self) -> None:
        '''Pushes the player to the center of the hookax.\n
           Spends player mana.\n'''
        if not self.pushing: return
        if not self.stats.spend(Entity.dt,self.push_cost,2): return

        Entity.player.pull(self.center(), self.speed_value)
#

#
    def deactivate(self) -> None:
        self.hitted_entity = None
        self.pulling = False
        self.pushing = False
        self.resetAction()
        return super().deactivate()

    def kill(self) -> None:
        self.speed_dir = pg.math.Vector2(0,0)
        return super().kill()

    def die(self) -> None:
        return self.deactivate()
#

    def fitInDisplayBounds(self) -> None:
        '''Hookax must not be fitted in display.\n'''
        return

    def checkInputs(self, events: list[pg.event.Event]) -> None:
        for ev in events:
            if ev.type == pg.KEYDOWN:
                if ev.key == 101:
                    self.pulling = True
                if ev.key == 114:
                    self.pushing = True

            elif ev.type == pg.KEYUP:
                if ev.key == 101:
                    self.pulling = False
                elif ev.key == 114:
                    self.pushing = False

    def blit(self) -> None:
        '''Makes the hookax spins and blits it.\n'''

        # rotating.
        if self.speed_dir == pg.math.Vector2(0,0) and not (self.pulling or self.pushing): 
            self.blit_angle = 0
        else: self.blit_angle -= Entity.dt*self.speed_value*4

        Entity.blitter.addLine(0, Entity.player.center(), self.center(), (40,80,30), 3)

        return super().blit()

    def update(self, events: list[pg.event.Event]) -> None:
        super().update()

        if not self.active: return

        self.pull()
        self.push()
        self.checkInputs(events)