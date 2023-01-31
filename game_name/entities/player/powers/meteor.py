import game_name.entities.power as pwr
from random import randint

meteor_sprite_path = 'assets/entities/player/powers/meteor.png'
explosion_sprite_path = 'assets/entities/player/powers/explosion.png'

class Meteor(pwr.Power):

    def __init__(self, pos: pwr.ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator = pwr.ent.an.Animator(pwr.ent.pg.image.load(meteor_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])
        self.animator.loadSprites(pwr.ent.pg.image.load(explosion_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])

        self.speed_value = 150

        self.hit_pos = pwr.ent.pg.math.Vector2()

    def activate(self) -> None:
        '''Meteor power activation.\n'''

        self.pos = pwr.ent.pg.math.Vector2(randint(-100,pwr.ent.pg.display.get_window_size()[0]+100), randint(-300,-200))

        self.hit_pos = pwr.ent.pg.mouse.get_pos()

        self.speed: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2( self.hit_pos - self.center() ).normalize()

        self.blit_angle = self.speed.angle_to(pwr.ent.pg.math.Vector2(0,1))

        super().activate()

    def update(self) -> None:
        if not self.activated:
            return
        
        self.animator.changeUpdateCoeficient(20)
        super().update()