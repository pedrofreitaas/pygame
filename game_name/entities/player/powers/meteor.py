from game_name.entities.power import *

meteor_sprite_path = 'assets/entities/player/powers/meteor.png'
meteor_icon_path = 'assets/entities/player/powers/meteor_icon.png'
explosion_sprite_path = 'assets/entities/player/powers/explosion.png'

meteor_sound_path = 'assets/entities/player/powers/sounds/flamethrower.ogg'
explosion_sound_path = 'assets/entities/player/powers/sounds/explode1.wav'

class Meteor(Power):
    meteor_sound = pg.mixer.Sound(meteor_sound_path)
    meteor_sound.set_volume(0.3)
    
    explosion_sound = pg.mixer.Sound(explosion_sound_path)
    explosion_sound.set_volume(0.2)

    def __init__(self) -> None:
        # entity's values.
        super().__init__(layer=2,speed_value=0,caster_stats=Entity.player.stats,damage=50,mana_cost=40,instant=False,cooldown=8)
        self.animator = an.Animator(pg.image.load(meteor_sprite_path).convert_alpha(),
                                    [100,100],
                                    [8,8,8,8,8,8,8,5])
        self.animator.loadSprites(pg.image.load(explosion_sprite_path).convert_alpha(),
                                  [100,100],
                                  [8,8,8,8,8,8,8,5])
        self.rect_adjust = [-50,-50]
        self.target: int = 1
        
        # meteor values.
        self.hit_time: float = 1.3
        self.explode_time: float = 2.5

        self.hit_pos: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.exploded: bool = False

        self.explode_timer_index: int = len(self.timers)
        self.timers.append(Timer(self.hit_time, lambda: self.explode(), -1))

        self.pos_explode_timer_index: int = len(self.timers)
        self.timers.append(Timer(self.explode_time, lambda: self.deactivate(), -1))

        self.trigger_key: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter('t', False) )
        self.trigger_key_pressed: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter('t', True) )

        self.trigger_image: pg.surface.Surface = pg.image.load(meteor_icon_path).convert_alpha()

        self.initialize()

    def __str__(self) -> str:
        return super().__str__()+'.meteor'

# .
    def setAngle(self) -> None:
        '''Sets the angle to rotate the meteor when moving to the target.\n'''
        image_dir = pg.math.Vector2(0,1)
        self.blit_angle = self.getMovementSpeed().angle_to(image_dir)

    def use(self) -> None:
        '''Meteor power activation.\n
           Activates the meteor hit timer of the instance.\n'''
        if not super().use(): return

        self.animator.setRange([0,60])
        self.exploded = False

        self.pos: pg.math.Vector2 = Entity.player.center() - pg.math.Vector2(0, 800)
        self.hit_pos: pg.math.Vector2 = pg.mouse.get_pos()-Entity.blitter.camera.getPos()

        self.setAngle()

        Meteor.meteor_sound.play(-1)

        self.timers[self.pos_explode_timer_index].deactiveTimer()

    def explode(self) -> None:
        '''Triggers meteor explosion.\n
           Triggers time for meteor deactivation.\n'''
        if self.exploded: return

        Meteor.meteor_sound.stop()
        Meteor.explosion_sound.play()

        self.exploded = True
        self.animator.setRange([60, self.animator.getTotalImages()-1])

        self.timers[self.pos_explode_timer_index].activateTimer()
# ------------------------------ #

# .
    def getLockMovement(self) -> bool:
        return False

    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Calculates the meteor speed to hit the target in the \'exact\' self.hit_time time.\n'''
        distance_vector = (self.hit_pos-self.center())

        total_loops = self.timers[self.explode_timer_index].timeLeft()/Entity.dt
        
        if total_loops != 0: self.complementSpeed( (distance_vector / total_loops) / Entity.dt )

        return super().getMovementSpeed()

    def move(self) -> None:
        '''Recalculates the speed of the meteor to reach the hit_pos according to hit time.\n
           Don't move if instance has exploded.\n'''       
        if self.exploded: return

        speed = self.getMovementSpeed()

        self.pos = self.pos + speed

        # reseting variables for nxt loop.
        self.speed_complement: pg.math.Vector2 = pg.math.Vector2()
# ------------------------------ #

# .
    def collisionUpdate(self) -> None:
        if not self.exploded: return
        super().collisionUpdate()
# ------------------------------ #

    def activeAndNotActiveBlitting(self) -> None:
        '''Blits the meteor interface.\n'''

        if not self.active and not self.in_cooldown and self.canUse():
            Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_key, (70,50) )
        else:
            Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_key_pressed, (70,50) )
        
        Entity.blitter.addImage(Entity.blitter.lastLayer(), self.trigger_image, (100,50) )

    def update(self) -> None:
        super().update()

        if not self.active: return

        if not self.exploded: self.animator.changeUpdateCoeficient(35)
