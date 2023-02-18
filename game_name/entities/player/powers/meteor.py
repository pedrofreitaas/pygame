import game_name.entities.power as pwr

meteor_sprite_path = 'assets/entities/player/powers/meteor.png'
explosion_sprite_path = 'assets/entities/player/powers/explosion.png'

meteor_sound_path = 'assets/entities/player/powers/sounds/flamethrower.ogg'
explosion_sound_path = 'assets/entities/player/powers/sounds/explode1.wav'

class Meteor(pwr.Power):
    meteor_sound = pwr.ent.pg.mixer.Sound(meteor_sound_path)
    meteor_sound.set_volume(0.3)
    
    explosion_sound = pwr.ent.pg.mixer.Sound(explosion_sound_path)
    explosion_sound.set_volume(0.2)

    def __init__(self, pos: pwr.ent.pg.math.Vector2, layer: int=2, speed_value: float=1) -> None:
        super().__init__(pos, layer, speed_value)
        
        self.hit_time: float = 3.2
        self.explode_time = 2.25

        self.animator = pwr.ent.an.Animator(pwr.ent.pg.image.load(meteor_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])
        self.animator.loadSprites(pwr.ent.pg.image.load(explosion_sprite_path).convert_alpha(), [100,100], [8,8,8,8,8,8,8,5])

        self.hit_pos = pwr.ent.pg.math.Vector2()

        self.layer: int = layer

        self.exploded: bool = False

        self.meteor_damage: float = 70

        self.rect_adjust = [-50,-50]

        # meteor hit/explode timers.
        self.timers.append(pwr.ent.Timer(self.hit_time, lambda: self.explode(), -1))
        self.pos_explosion_timer: pwr.ent.Timer = pwr.ent.Timer(self.explode_time, lambda: self.deactivate(), -1)
        
        # instance begin's deactived.
        self.deactivate()

# .
    def setAngle(self) -> None:
        '''Sets the angle to rotate the meteor when moving to the target.\n'''
        image_dir = pwr.ent.pg.math.Vector2(0,1)
        self.blit_angle = self.getMovementSpeed().angle_to(image_dir)

    def activate(self) -> None:
        '''Meteor power activation.\n
           Activates the meteor hit timer of the instance.\n'''
        if self.active: return

        self.animator.setRange([0,60])
        self.exploded = False

        self.pos: pwr.ent.pg.math.Vector2 = pwr.ent.Entity.player.center() - pwr.ent.pg.math.Vector2(0, 800)
        self.hit_pos: pwr.ent.pg.math.Vector2 = pwr.ent.pg.mouse.get_pos()-pwr.ent.Entity.blitter.camera.getPos()

        self.setAngle()

        Meteor.meteor_sound.play(-1)

        super().activate()

    def explode(self) -> None:
        '''Triggers meteor explosion, if the instance didn't explode yet and is close enought to it's hit pos.\n'''
        if self.exploded: return

        Meteor.meteor_sound.stop()
        Meteor.explosion_sound.play()

        self.exploded = True
        self.animator.setRange([60, self.animator.getTotalImages()-1])

        self.pos_explosion_timer.activateTimer()

    def deactivate(self) -> None:
        super().deactivate()
        self.pos_explosion_timer.deactiveTimer()
# ------------------------------ #

# .
    def getLockMovement(self) -> bool:
        return False

    def getMovementSpeed(self) -> pwr.ent.pg.math.Vector2:
        '''Calculates the meteor speed to hit the target in the \'exact\' self.hit_time time.\n'''
        distance_vector = (self.hit_pos-self.center())

        total_loops = self.timers[0].timeLeft()/pwr.ent.Entity.dt
        
        if total_loops != 0: self.complementSpeed( (distance_vector / total_loops) / pwr.ent.Entity.dt )

        return super().getMovementSpeed()

    def move(self) -> None:
        '''Recalculates the speed of the meteor to reach the hit_pos according to hit time.\n
           Don't move if instance has exploded.\n'''
        if self.exploded: return

        speed = self.getMovementSpeed()

        # reseting variables for nxt loop.
        self.speed_complement: pwr.ent.pg.math.Vector2 = pwr.ent.pg.math.Vector2()

        self.pos = self.pos + speed
# ------------------------------ #

# .
    def collisionUpdate(self) -> None:
        super().collisionUpdate()

        if not self.exploded: return

        for en in pwr.ent.Entity.enemies:
            if self.rect.colliderect(en.rect):
                en.damageSelf(self.meteor_damage)
# ------------------------------ #

    def update(self) -> None:
        if not self.active:
            return

        if not self.exploded: self.animator.changeUpdateCoeficient(35)
        else: pwr.ent.updateTimers( [self.pos_explosion_timer] )

        super().update()