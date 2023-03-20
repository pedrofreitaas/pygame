from game_name.entities.power import *

sprites_path = ['assets/entities/enemies/earthmonk/bulldoze.png']

class Bulldoze(Power):
    
    def __init__(self, caster_stats: Stats) -> None:
        super().__init__(layer=1, speed_value=150, caster_stats=caster_stats,damage=60,range=200,mana_cost=80,cooldown=8)

        self.target: int = 2

        self.animator: an.Animator = an.Animator(pg.image.load(sprites_path[0]).convert_alpha(),
                                           [50,50],
                                           [6])

        self.kill_timer_index: int = len(self.timers)
        self.timers.append( Timer(4, lambda: self.kill(), -1) )

        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.bulldoze'

#
    def use(self, earth_monk_center: pg.math.Vector2, distance_to_target_squared) -> bool:
        if not super().use(distance_to_target_squared): return
        self.pos = earth_monk_center - (pg.math.Vector2(self.animator.currentSpriteSize())/2)

        self.speed_dir = Entity.player.center() - self.center()
        if self.speed_dir != pg.math.Vector2(0,0): self.speed_dir.normalize_ip()

    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == -1:
            self.animator.setRange((1,6))
            self.animator.setEAP(lambda:self.die())
            return

        self.animator.setRange((0,1))

    def die(self) -> None:
        self.deactivate()
        self.resetAction()

    def blit(self) -> None:
        self.blit_angle += 0.88
        if self.blit_angle > 360: self.blit_angle = 0

        return super().blit()