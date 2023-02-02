import game_name.entities.power as pwr
from random import randint

meteor_sprite_path = 'assets/entities/player/powers/meteor.png'
explosion_sprite_path = 'assets/entities/player/powers/explosion.png'

class Meteor(pwr.Power):

    def __init__(self, pos: pwr.ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator = pwr.ent.an.Animator(pwr.ent.pg.image.load(meteor_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])
        self.animator.loadSprites(pwr.ent.pg.image.load(explosion_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])

        self.hit_pos = pwr.ent.pg.math.Vector2()
        
        self.hit_time: float = 2.25
        self.explode_time = 0.75

        self.exploded: bool = False

        # meteor hit/explode timers.
        self.timers: list[pwr.ent.Timer] = [pwr.ent.Timer(self.hit_time, lambda: self.explode(), -1), pwr.ent.Timer(self.explode_time, lambda: self.deactive(), -1)]
        
        # instance begin's deactived.
        self.deactive()

    def activate(self) -> None:
        '''Meteor power activation.\n
           Activates the meteor hit timer of the instance.\n'''
        if self.activated: return

        self.animator.setRange([0,60])
        self.exploded = False

        self.pos: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2(randint(-100,pwr.ent.pg.display.get_window_size()[0]+100), randint(-400,-300))
        self.hit_pos: pwr.ent.pg.math.Vector2 = pwr.ent.pg.mouse.get_pos()

        self.timers[0].activateTimer()
        super().activate()

        self.calculateSpeed()
        self.setAngle()

    def deactive(self) -> None:
        '''Deactivates instance and it's timers.\n'''
        self.timers[0].deactiveTimer()
        self.timers[1].deactiveTimer()
        super().deactive()

    def calculateSpeed(self) -> None:
        '''Calculates the meteor speed to hit the target in the \'exact\' self.hit_time time.\n'''
        distance_vector = (self.hit_pos-self.center())

        total_loops = self.timers[0].timeLeft()/pwr.ent.Entity.dt
        
        if total_loops == 0: return # prevent zeroDivisionError.

        self.speed: pwr.ent.pg.math.Vector2 = distance_vector / total_loops

    def move(self) -> None:
        '''Recalculates the speed of the entity to reach the hit_pos according to hit time.\n
           Don't move if instance has exploded.\n'''
        if self.exploded: return

        self.calculateSpeed()

        if not self.blockMove_H: self.pos[0] = self.pos[0] + self.speed[0]
        if not self.blockMove_V: self.pos[1] = self.pos[1] + self.speed[1]
    
    def setAngle(self) -> None:
        '''Sets the angle to rotate the meteor when moving to the target.\n'''
        image_dir = pwr.ent.pg.math.Vector2(0,1)
        self.blit_angle = self.speed.angle_to(image_dir)

    def explode(self) -> None:
        '''Triggers meteor explosion, if the instance didn't explode yet and is close enought to it's hit pos.\n'''

        if self.exploded: return

        self.exploded = True
        self.animator.setRange([60, self.animator.getTotalImages()-1])

        self.timers[1].activateTimer()

    def update(self) -> None:
        if not self.activated:
            return

        if not self.exploded: self.animator.changeUpdateCoeficient(35)

        super().update()