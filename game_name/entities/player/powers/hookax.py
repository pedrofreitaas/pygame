from game_name.entities.power import *

spritesheet = ['assets/entities/player/powers/hookax.png']

class Hookax(Power):
    def __init__(self) -> None:
        super().__init__(layer=2, speed_value=250, caster_stats=Entity.player.stats, damage=0, mana_cost=15, stamina_cost=0, range=0, instant=False, cooldown=3, effect=None)

        self.animator = an.Animator( pg.image.load(spritesheet[0]).convert_alpha(),
                                     (80,80),
                                     [1] )
        
        self.hit_pos: pg.math.Vector2 = self.pos
        
        self.animator.resizeSprites( (40,40) )

        self.rotate: bool = True

        self.hitted_entity: Entity = None
        # self.hitted_structure:

        self.target: int = 1
        
        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.hookax'
        
    def use(self) -> bool:
        if not super().use(): return
        self.pos = Entity.player.center()- (pg.math.Vector2( self.animator.currentSpriteSize() )/2)
        self.rotate = True
        self.hit_pos = pg.mouse.get_pos()- Entity.blitter.camera.getPos()
        self.speed_dir = (self.hit_pos-self.pos).normalize()

    def collideEnemies(self) -> None:
        for en in Entity.enemies:
            if self.damage_rect.colliderect(en.rect):

                if self.mask.overlap_area(en.mask, en.pos-self.pos) <= 0: continue

                self.rotate = False
                self.hitted_entity = en
                self.hit_pos = en.pos
        
        return super().collideEnemies()

    def move(self) -> None:
        if self.hitted_entity != None: 
            delta_pos = self.hitted_entity.pos-self.hit_pos
            self.pos = self.pos + delta_pos
            self.hit_pos = self.hitted_entity.pos
            return

        return super().move()
    
    def deactivate(self) -> None:
        self.hitted_entity = None
        return super().deactivate()

    def update(self) -> None:
        super().update()

        if not self.active: return

        if self.rotate: self.blit_angle -= Entity.dt*self.speed_value*2
        else: self.blit_angle = 0