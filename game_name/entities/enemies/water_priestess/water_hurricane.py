from game_name.entities.power import *
from random import randint
from math import sin, cos

sprites_path = ['assets/entities/enemies/waterpriestess/waterHurricane_start.png',
                'assets/entities/enemies/waterpriestess/waterHurricane_end.png' ]

class WaterHurricane(Power):
    def __init__(self) -> None:
        super().__init__(layer=2, speed_value=130, damage=20, mana_cost=50, stamina_cost=0, damage_is_instant=False, cooldown=6, effect=None)

        self.target: int = 2

        self.animator: an.Animator = an.Animator(pg.image.load(sprites_path[0]).convert_alpha(),
                                           [128,128],
                                           [4,4,4])
        
        self.animator.loadSprites(pg.image.load(sprites_path[1]).convert_alpha(),
                                  [128,128],
                                  [3,3,2])

        self.rect_adjust: tuple[float,float] = [-90, -40]

        self.timers.append( Timer(8, lambda: self.kill(), -1) )

        self.parameter: float = 0
        
        self.current_attack = Attack(damage=20, mana_cost=50, stamina_cost=30)
        self.attacks.append(self.current_attack)

    def activate(self) -> None:
        if self.active: return

        super().activate()

        self.pos = Entity.player.pos - pg.math.Vector2(randint(30,80), randint(30,80))

    def die(self) -> None:
        '''Deactives the waterHurricane power and resets action.\n'''
        self.action = 0
        self.deactivate()

    def damageSelf(self) -> None:
        '''Water_hurricane power doesn't take damage.\n'''
    
    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == -1: self.animator.setRange([12,19])
        else: self.animator.setRange([0,12])

    def move(self) -> None:
        '''WaterHurricane movement method.\n
           Same as entity's movement, but without fitInDisplayBounds method.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()

    def update(self) -> None:
        if not self.active: return

        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(-1.4*sin(self.parameter), 2.5*cos(self.parameter)).rotate(30)
        
        self.parameter+=0.01
        if self.parameter>=6.28: 
            self.parameter = 0
            
        super().update()
