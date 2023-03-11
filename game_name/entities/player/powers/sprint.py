from game_name.entities.power import *
from game_name.game_map.structure import *
from math import sin,cos

spritesheet = ['assets/entities/player/powers/sprint.png',
               'assets/entities/player/powers/sprint_icon.png']

class Sprint(Power):
    def __init__(self) -> None:
        super().__init__(Entity.player.layer, speed_value=0, caster_stats=Entity.player.stats, damage=0, mana_cost=4, range=0, stamina_cost=15, instant=False, cooldown=4, effect=None)

        self.animator = an.Animator( pg.image.load(spritesheet[0]).convert_alpha(),
                                     (48,48),
                                     [6])
        
        self.intermidiate_layer: int = self.layer

        self.speed_boost: float = 200

        self.parameter: float = 0

        self.trigger_key: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter('q', False) )
        self.trigger_key_pressed: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter('q', True) )

        self.trigger_image: pg.surface.Surface = pg.image.load(spritesheet[1]).convert_alpha()
        
        self.initialize()

    def use(self) -> bool:
        if not super().use(): return
        Entity.player.speed_value += self.speed_boost
    
    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animator.setRange((0,5))

    def move(self) -> None:
        self.pos = Entity.player.pos + pg.math.Vector2(Entity.player.mask.centroid()) - (pg.math.Vector2(self.animator.currentSpriteSize())/2)
        self.pos = self.pos + pg.math.Vector2( cos(self.parameter)*15, sin(self.parameter)*5)

        self.parameter += 0.05

        if self.parameter < 3.14: self.layer = self.intermidiate_layer
        else: self.layer = self.intermidiate_layer+1

        if self.parameter > 6.28: self.parameter = 0
    
    def turnOff(self) -> None:
        Entity.player.speed_value -= self.speed_boost
        self.deactivate()

    def checkInputs(self, events: list[pg.event.Event]) -> None:
        for ev in events:
            if ev.type == pg.KEYUP and ev.key == 113: #ord('q')
                self.turnOff()

    def activeAndNotActiveBlitting(self) -> None:
        
        if not self.active and not self.in_cooldown and self.canUse():
            Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_key, (135,50))
        else:
            Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_key_pressed, (135,50))

        Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_image, (165,50))

    def update(self, events: list[pg.event.Event]) -> None:
        super().update()

        if not self.active: return

        self.checkInputs(events)
        if not self.stats.spend(Entity.dt, self.current_attack.mana_cost, 2) or not self.stats.spend(Entity.dt, self.current_attack.stamina_cost, 3):
            self.turnOff()
