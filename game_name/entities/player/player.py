import game_name.entities.entity as ent
import game_name.entities.player.powers.meteor as meteor

player_sprites_path = ['assets/entities/player/char_red_1.png', 'assets/entities/player/char_red_2.png' ]
player_sounds_path = ['assets/entities/player/sounds/footsteps.ogg', 'assets/entities/player/sounds/hit.wav']

class Player( ent.Entity ):
    footstep_sound = ent.pg.mixer.Sound(player_sounds_path[0])
    footstep_sound.set_volume(0.0125)

    hit_sound = ent.pg.mixer.Sound(player_sounds_path[1])
    hit_sound.set_volume(0.08)
    
    def __init__(self, pos: ent.pg.math.Vector2, layer: int=1, speed_value: float=120) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator: ent.an.Animator = ent.an.Animator( ent.pg.image.load(player_sprites_path[0]).convert_alpha(),
                                                          [56,56],
                                                          [6,8,8,8,8,4,8,4,8,3,3])

        self.animator.loadSprites( ent.pg.image.load(player_sprites_path[1]).convert_alpha(),
                                                          [56,56],
                                                          [8,2,8,4,8,8,2] )

        ent.Entity.player = self

        self.meteor: meteor.Meteor = meteor.Meteor(ent.pg.math.Vector2(), self.layer, 100)

        self.rect_adjust: tuple = [-20,-20]

    def animationAction(self) -> None:
        '''Sets actions for the player according to the current animation stage.\n'''
        if self.action == 1: # attacking            
            if int(self.animator.index_image) in [9,12,16]:
                # attack sound.
                Player.hit_sound.play()

                # attack movement.
                self.complementSpeed(self.speed_dir*self.speed_value*ent.Entity.dt)
                    
            else: Player.hit_sound.stop()

        elif self.action == 2: # deffending
            pass       

        elif self.action == 3: # casting
            self.animator.setEAP(lambda: self.launchMeteor())
        
        if self.isMoving(): Player.footstep_sound.play()
        else: Player.footstep_sound.stop()

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()

        if self.action == 1:
            self.animator.setRange([6,23])
            return

        if self.action == 2:
            self.animator.setRange([65,68])
            self.animator.activateStopAtEnd()
            return

        if self.action == 3:
            self.animator.setRange([54,62])
            return

        if self.isMoving():
            self.animator.setRange([38,42])
            return
        
        #idle animation.
        self.animator.setRange([0,5])

    def checkInputs(self, events: list[ent.pg.event.Event]) -> None:
        '''Check keyboard and mouse inputs.\n'''

        for ev in events:

            if ev.type == ent.pg.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    self.attack()

                elif ev.button == 3:
                    self.defend()

            if ev.type == ent.pg.MOUSEBUTTONUP:
                if ev.button in [1,3]:
                    self.resetAction()

            if ev.type == ent.pg.KEYDOWN:
                
                if ev.key == 119: #ord('w')
                    self.speed_dir[1] -= 1

                elif ev.key == 115: #ord('s')
                    self.speed_dir[1] += 1

                elif ev.key == 97: #ord('a')
                    self.speed_dir[0] -= 1

                elif ev.key == 100: #ord('d')
                    self.speed_dir[0] += 1

                elif ev.key == 101: #ord('e')
                    self.cast()
            
            if ev.type == ent.pg.KEYUP:
                
                if ev.key == 119: #ord('w')
                    self.speed_dir[1] += 1

                elif ev.key == 115: #ord('s')
                    self.speed_dir[1] -= 1

                elif ev.key == 97: #ord('a')
                    self.speed_dir[0] += 1

                elif ev.key == 100: #ord('d')
                    self.speed_dir[0] -= 1

                elif ev.key == 101: #ord('e')
                    self.resetAction()

    def update(self, events: list[ent.pg.event.Event]) -> None:
        self.checkInputs(events)

        self.animationAction()

        self.meteor.update()

        super().update()

# power methods.
    def launchMeteor(self) -> None:
        self.meteor.activate()
        self.resetAction()