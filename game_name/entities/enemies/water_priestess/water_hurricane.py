import game_name.entities.power as pwr
from random import randint
from math import sin, cos

sprites_path = ['assets/entities/enemies/waterpriestess/waterHurricane_start.png',
                'assets/entities/enemies/waterpriestess/waterHurricane_end.png' ]

class WaterHurricane(pwr.Power):
    def __init__(self, pos: pwr.ent.pg.math.Vector2) -> None:
        super().__init__(pos, 2, 30)

        self.animator: pwr.ent.an.Animator = pwr.ent.an.Animator(pwr.ent.pg.image.load(sprites_path[0]).convert_alpha(),
                                           [128,128],
                                           [4,4,4])
        
        self.animator.loadSprites(pwr.ent.pg.image.load(sprites_path[1]).convert_alpha(),
                                  [128,128],
                                  [3,3,2])

        self.rect_adjust: tuple[float,float] = [-90, -40]

        self.timers.append( pwr.ent.Timer(8, lambda: self.kill(), -1) )

        self.speed_value: float = 130

        self.attack_damage: float = 20

        self.parameter: float = 0

        # pwr begin's deactivated.
        self.deactivate()

    def activate(self) -> None:
        if self.active: return

        super().activate()

        self.pos = pwr.ent.Entity.player.pos - pwr.ent.pg.math.Vector2(randint(30,80), randint(30,80))

    def die(self) -> None:
        '''Deactives the waterHurricane power and resets action.\n'''
        self.action = 0
        self.deactivate()

    def damageSelf(self, value: float, instant=False) -> None:
        '''Water_hurricane power doesn't take damage.\n'''
    
    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == -1: self.animator.setRange([12,19])
        else: self.animator.setRange([0,12])
        
    def collisionUpdate(self) -> None:
        super().collisionUpdate()

        if self.rect.colliderect(pwr.ent.Entity.player):
            pwr.ent.Entity.player.damageSelf(self.attack_damage)

    def move(self) -> None:
        '''WaterHurricane movement method.\n
           Same as entity's movement, but without fitInDisplayBounds method.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        # reseting variables for nxt loop.
        self.speed_complement: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2()

    def update(self) -> None:
        if not self.active: return

        self.speed_dir: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2(-1.4*sin(self.parameter), 2.5*cos(self.parameter)).rotate(30)
        
        self.parameter+=0.01
        if self.parameter>=6.28: 
            self.parameter = 0
            
        super().update()