from game_name.entities.power import *
from random import randint
from math import sin, cos

sprites_path = ['assets/entities/enemies/waterpriestess/waterHurricane_start.png',
                'assets/entities/enemies/waterpriestess/waterHurricane_end.png' ]

class WaterHurricane(Power):
    
    def __init__(self, caster_stats: Stats) -> None:
        super().__init__(layer=2, speed_value=130, caster_stats=caster_stats,damage=20,range=160,mana_cost=20,stamina_cost=0,instant=False,cooldown=6,effect=None)

        self.target: int = 2

        self.animator: an.Animator = an.Animator(pg.image.load(sprites_path[0]).convert_alpha(),
                                           [128,128],
                                           [4,4,4])
        
        self.animator.loadSprites(pg.image.load(sprites_path[1]).convert_alpha(),
                                  [128,128],
                                  [3,3,2])

        self.rect_adjust: tuple[float,float] = (-90, -40)

        self.kill_timer_index: int = len(self.timers)
        self.timers.append( Timer(8, lambda: self.kill(), -1) )

        self.parameter: float = 0

        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.water_hurricane'

#
    def use(self, distance_to_target_squared: float=0) -> bool:
        if not super().use(distance_to_target_squared): return
        self.pos = Entity.player.pos - pg.math.Vector2(randint(30,80), randint(30,80))

    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == -1: self.animator.setRange((12,19))
        else: self.animator.setRange((0,12))

    def move(self) -> None:
        '''WaterHurricane movement method.\n
           Same as entity's movement, but without fitInDisplayBounds method.\n'''
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(-1.4*sin(self.parameter), 2.5*cos(self.parameter)).rotate(30)
        
        self.parameter+=0.01
        if self.parameter>=6.28: 
            self.parameter = 0

        self.pos = self.pos + self.getMovementSpeed()

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()

    def kill(self) -> None:
        return super().kill()

    def die(self) -> None:
        self.deactivate()
        self.resetAction()
