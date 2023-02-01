import game_name.entities.power as pwr
from random import randint

meteor_sprite_path = 'assets/entities/player/powers/meteor.png'
explosion_sprite_path = 'assets/entities/player/powers/explosion.png'

class Meteor(pwr.Power):

    def __init__(self, pos: pwr.ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator = pwr.ent.an.Animator(pwr.ent.pg.image.load(meteor_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])
        self.animator.loadSprites(pwr.ent.pg.image.load(explosion_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])

        self.speed_value: float = 150

        self.hit_pos = pwr.ent.pg.math.Vector2()
        self.hit_time: float = 2.25

        self.exploded: bool = False

    def calculateSpeed(self) -> None:
        '''Calculates the meteor speed to hit the target in the \'exact\' given time.\n'''

        distance_vector = (self.hit_pos-self.center())
        coeficient = self.hit_time / pwr.ent.Entity.dt

        self.speed_value = distance_vector.length() / coeficient / pwr.ent.Entity.dt
        self.speed: pwr.ent.pg.math.Vector2 = distance_vector.normalize()
    
    def activate(self) -> None:
        '''Meteor power activation.\n'''

        self.animator.setRange([0,60])

        self.exploded = False

        self.pos: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2(randint(-100,pwr.ent.pg.display.get_window_size()[0]+100), randint(-300,-200))
        self.hit_pos: pwr.ent.pg.math.Vector2 = pwr.ent.pg.mouse.get_pos()
        self.calculateSpeed()

        self.blit_angle = self.speed.angle_to(pwr.ent.pg.math.Vector2(0,1))

        super().activate()

        # explosion timer.
        self.timers.append(pwr.ent.Timer(self.hit_time, lambda: self.explode(), True))

    def explode(self) -> None:
        '''Triggers meteor explosion.\n'''
        self.exploded = True
        self.animator.setRange([60, self.animator.getTotalImages()-1])
        self.speed = pwr.ent.pg.math.Vector2()

        self.timers.append(pwr.ent.Timer(0.75, lambda: self.deactive(), True))

    def center(self) -> pwr.ent.pg.math.Vector2:
        '''Returns a vector to the center of the meteor.\n'''
        return self.pos + pwr.ent.pg.math.Vector2(53,53)

    def update(self) -> None:
        if not self.activated:
            return
        
        if not self.exploded: self.animator.changeUpdateCoeficient(35)

        super().update()