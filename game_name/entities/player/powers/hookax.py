from game_name.entities.power import *
from game_name.game_map.structure import *

spritesheet = ['assets/entities/player/powers/hookax.png']

class Hookax(Power):
    def __init__(self) -> None:
        super().__init__(layer=2, speed_value=250, caster_stats=Entity.player.stats, damage=1, mana_cost=15, stamina_cost=0, range=0, instant=False, cooldown=3, effect=None)

        self.animator = an.Animator( pg.image.load(spritesheet[0]).convert_alpha(),
                                     (80,80),
                                     [1] )
        
        self.hit_pos: pg.math.Vector2 = self.pos

        self.pull_cost: float = 15.8
        self.push_cost: float = 10
        
        self.animator.resizeSprites( (40,40) )

        self.rotate: bool = True
        self.pulling: bool = False
        self.pushing: bool = False

        self.hitted_entity: Entity|None = None
        self.vec: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.hitted_struct: bool = False

        self.target: int = 3
        
        self.active_time: float = 10
        self.timers.append(Timer(self.active_time, lambda: self.deactivate(), -1))

        self.max_speed_value: float = self.speed_value
        self.slow_factor: float = 70
        
        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.hookax'
        
    def setTarget(self) -> None:
        self.speed_value = self.max_speed_value
        self.rotate = True
        self.hit_pos = pg.mouse.get_pos()- Entity.blitter.camera.getPos()
        self.speed_dir = (self.hit_pos-self.pos).normalize()

    def use(self) -> bool:
        if not super().use(): return

        self.hitted_entity = None
        self.hitted_struct = False
        self.pos = Entity.player.center()- (pg.math.Vector2( self.animator.currentSpriteSize() )/2)
        
        self.setTarget()

#
    def collisionUpdate(self) -> None:
        super().collisionUpdate()
        self.collideStructs()

    def collideEnemies(self) -> None:
        '''If hookax hasn't collided yet and is moving, verifies enemy collision and sticks the hookax to the hitted enemy.\n'''
        if self.hitted_entity != None or self.hitted_struct: return
        if not self.isMoving(): return

        for en in Entity.enemies:
            if self.damage_rect.colliderect(en.rect):

                if self.mask.overlap_area(en.mask, en.pos-self.pos) <= 0: continue

                self.rotate = False
                self.hitted_entity = en
                self.vec = self.center()-en.center()
                
                break

    def collideStructs(self) -> None:
        '''If hookax hasn't collided yet and it's moving, verifies collision with structures.\n'''
        if self.hitted_entity != None: return
        if not Entity.map.structExists(self.rect, 1): return
        if not self.isMoving(): return

        self.hitted_struct = True
        self.rotate = False
#

    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        self.animator.setRange((0,1))

#
    def move(self) -> None:
        if self.hitted_entity != None: 
            self.pos = self.hitted_entity.center()-self.vec
            return
        
        elif self.hitted_struct:
            return

        self.speed_value -= Entity.dt*self.slow_factor
        if self.speed_value < 0: self.speed_value = 0
        return super().move()
    
    def pull(self) -> None:
        '''If the hookax has hit an entity, pulls it to the player.\n
           Spends player mana.\n'''
        if not self.isMoving() and self.pulling:
            self.setTarget()
            return

        if self.hitted_entity == None or not self.pulling: return
        if not self.stats.hasEnough(self.pull_cost,2): return

        self.useMana(self.pull_cost, False)
        self.hitted_entity.pull(Entity.player.center())

    def push(self) -> None:
        '''If the hookax has hit an structure, pulls the player to it.\n
           Spends player mana.\n'''
        if not self.hitted_struct or not self.pushing: return
        if not self.stats.hasEnough(self.push_cost,2): return

        self.useMana(self.push_cost, False)
        Entity.player.pull(self.center())
#

    def deactivate(self) -> None:
        self.hitted_entity = None
        return super().deactivate()

    def checkInputs(self, events: list[pg.event.Event]) -> None:
        for ev in events:
            if ev.type == pg.KEYDOWN:
                if ev.key == 101:
                    if self.hitted_struct: self.pushing = True
                    else: self.pulling = True

            elif ev.type == pg.KEYUP:
                if ev.key == 101:
                    self.pulling = False
                    self.pushing = False

    def update(self, events: list[pg.event.Event]) -> None:
        super().update()

        if not self.active: return

        self.pull()
        self.push()
        self.checkInputs(events)

        if self.rotate: self.blit_angle -= Entity.dt*self.speed_value*2
        else: self.blit_angle = 0