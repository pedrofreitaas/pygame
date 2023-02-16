import game_name.entities.entity as ent
import game_name.entities.player.powers.meteor as meteor

player_sprites_path = ['assets/entities/player/char_red_1.png', 'assets/entities/player/char_red_2.png' ]
player_sounds_path = ['assets/entities/player/sounds/footsteps.ogg', 'assets/entities/player/sounds/hit.wav']

class Player( ent.Entity ):
    footstep_sound = ent.pg.mixer.Sound(player_sounds_path[0])
    footstep_sound.set_volume(0.0125)

    hit_sound = ent.pg.mixer.Sound(player_sounds_path[1])
    hit_sound.set_volume(0.08)
    
    def __init__(self, pos: ent.pg.math.Vector2, layer: int=1, speed_value: float=160) -> None:
        super().__init__(pos, layer, speed_value, 80, 40, 120)

        self.animator: ent.an.Animator = ent.an.Animator( ent.pg.image.load(player_sprites_path[0]).convert_alpha(),
                                                          [56,56],
                                                          [6,8,8,8,8,4,8,4,8,3,3])

        self.animator.loadSprites( ent.pg.image.load(player_sprites_path[1]).convert_alpha(),
                                                          [56,56],
                                                          [8,2,8,4,4,8,2] )

        ent.Entity.player = self

        self.meteor: meteor.Meteor = meteor.Meteor(ent.pg.math.Vector2(), self.layer, 100)

        self.rect_adjust: tuple = [-30,-20]

        self.attack_damage: float = 40

        self.slide_speed: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)

        self.setStatsSurfaces()

    def setStatsSurfaces(self) -> None:
        '''Sets the surface that represents the player's stats.\n'''

        self.life_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_life,10))
        self.life_surface.fill((200,0,0))

        self.mana_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_mana, 6))
        self.mana_surface.fill((0,0,180))

        self.stamina_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_stamina, 8))
        self.stamina_surface.fill((0,200,0))

    def animationAction(self) -> None:
        '''Sets actions for the player according to the current animation stage.\n'''
        super().animationAction()

        if self.action == 1: # attacking            
            if int(self.animator.index_image) in [9,12,16]:
                # attack sound.
                Player.hit_sound.play()

                # attack movement.
                self.complementSpeed(self.speed_dir*self.speed_value)
                    
            else: Player.hit_sound.stop()

        elif self.action == 2: # deffending
            pass       

        elif self.action == 3: # casting
            self.animator.setEAP(lambda: self.launchMeteor())
        
        elif self.action == 4: # sliding
            self.complementSpeed(self.slide_speed)
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*2)
            self.animator.setEAP(lambda: self.resetAction())
        
        if self.isMoving(): Player.footstep_sound.play()
        else: Player.footstep_sound.stop()

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()

        if self.action == -1:
            self.animator.setRange([43,54])
            return

        if self.stats.is_taking_damage:
            self.animator.setRange([90,93])
            self.animator.activateStopAt(0.8)
            return

        if self.action == 1:
            self.animator.setRange([6,23])
            return

        if self.action == 2:
            self.animator.setRange([65,68])
            self.animator.activateStopAt(0.5)
            return

        if self.action == 3:
            self.animator.setRange([54,62])
            return

        if self.action == 4:
            self.animator.setRange([78,86])
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

                elif ev.key == ent.pg.K_SPACE:
                    self.slide()
            
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

    def attack(self) -> None:
        '''Toogles player's attack, if possible.\n'''
        if self.action == 0 and not self.stats.is_taking_damage:
            self.action = 1

    def defend(self) -> None:
        '''Toggles player's defense, if possible.\n'''
        if self.action == 0 and not self.stats.is_taking_damage:
            self.action = 2

    def cast(self) -> None:
        '''Toggles player's casting, if possible.\n'''
        if self.action == 0 and not self.stats.is_taking_damage:
            self.action = 3

    def slide(self) -> None:
        '''Make the player slide.\n'''
        if self.action == 0 and not self.stats.is_taking_damage and self.stats.hasEnough(30, 3):
            self.action = 4
            self.stats.spend(1, 20, 3)

            if self.speed_dir == ent.pg.math.Vector2(): self.slide_speed = self.speed_dir

            else: self.slide_speed = self.speed_dir.normalize()*self.speed_value*1.2

    def getLifeSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,10)

    def getManaSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,21)

    def getStaminaSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,28)

    def blitStats(self) -> None:
        '''Blits player stats.\n
           Life+Mana+Stamina.\n'''

        ent.Entity.blitter.addNonTile(ent.Entity.blitter.lastLayer(),
                                           self.life_surface.subsurface((0,0), (self.stats.life, 10)),
                                           self.getLifeSurfacePos())

        ent.Entity.blitter.addNonTile(ent.Entity.blitter.lastLayer(), 
                                           self.mana_surface.subsurface((0,0), (self.stats.mana, 6)),
                                           self.getManaSurfacePos())

        ent.Entity.blitter.addNonTile(ent.Entity.blitter.lastLayer(), 
                                           self.stamina_surface.subsurface((0,0), (self.stats.stamina, 8)),
                                           self.getStaminaSurfacePos())

    def damageSelf(self, value: float, instant=False) -> None:
        '''Damages the player.\n
           If defending inflicts reduced damage to life, but damages stamina.\n'''

        if instant: dt = 1
        else: dt = ent.Entity.dt
        
        if self.action == 2: # defending.
            self.stats.spend(dt, value*0.2, 1)
            self.stats.spend(dt, value*0.6, 3)

            return

        self.stats.spend(dt, value, 1)
        self.stats.spend(dt, value*0.2, 3)

    def collisionUpdate(self) -> None:
        super().collisionUpdate()

        if self.action != 1: return

        for en in ent.Entity.enemies:
            if self.rect.colliderect(en.rect):
                en.damageSelf(self.attack_damage)

    def update(self, events: list[ent.pg.event.Event]) -> None:
        if self.is_dead: return

        self.checkInputs(events)

        self.animationAction()

        self.meteor.update()

        super().update()

# power methods.
    def launchMeteor(self) -> None:
        if self.stats.hasEnough(40, 2):
            self.meteor.activate()
            self.useMana(40,True)
        self.resetAction()