import game_name.entities.entity as ent
import game_name.entities.player.powers.meteor as meteor
from game_name.entities.player.powers.sprint import *
from game_name.entities.player.powers.hookax import *
from io import open

player_sprites_path = ['assets/entities/player/char_red_1.png', 'assets/entities/player/char_red_2.png' ]
player_sounds_path = ['assets/entities/player/sounds/footsteps.ogg',
                       'assets/entities/player/sounds/hit.wav',
                       'assets/entities/player/sounds/hurt.wav']

class Player( ent.Entity ):
    footstep_sound = ent.pg.mixer.Sound(player_sounds_path[0])
    footstep_sound.set_volume(0.025)

    hit_sound = ent.pg.mixer.Sound(player_sounds_path[1])
    hit_sound.set_volume(0.08)

    hurt_sound = ent.pg.mixer.Sound(player_sounds_path[2])
    hurt_sound.set_volume(0.09)

#
    def infoCode() -> str:
        return Entity.infoCode()+'.player'

    @classmethod
    def createInstanceWithDict(cls: 'Player', entInfos: dict) -> None:
        '''Creates Player's instance based on the entity's info inside the dict.\n'''        
        Entity.player = cls( pg.math.Vector2(entInfos['x'], entInfos['y']) )

    @classmethod
    def saveEmptyDict(cls: 'Player') -> None:
        '''Saves empty dict of player in game_info's file and creates a new player.\n'''
        Entity.player = Player(pg.math.Vector2(20,20))
#

    def __init__(self, pos: ent.pg.math.Vector2) -> None:
        super().__init__(pos, 1, 120, 80, 40, 120)

        self.animator: ent.an.Animator = ent.an.Animator( ent.pg.image.load(player_sprites_path[0]).convert_alpha(),
                                                          [56,56],
                                                          [6,8,8,8,8,4,8,4,8,3,3])

        self.animator.loadSprites( ent.pg.image.load(player_sprites_path[1]).convert_alpha(),
                                                          [56,56],
                                                          [8,2,8,4,4,8,2] )

        self.rect_adjust: tuple = [-30,-20]
        self.attacks: list[ent.Attack] = [ ent.Attack(damage=0, stamina_cost=20) ]
        self.target: int = 1

        # player variables.
        self.slide_speed: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)

        self.stats.setRegenFactor(3,1)
        self.stats.setRegenFactor(4,2)
        self.stats.setRegenFactor(22,3)

        self.speed_boost: float = 160
        ent.Entity.player = self

        # powers
        self.meteor: meteor.Meteor = meteor.Meteor()
        self.hookax: None|Hookax = None
        self.Sprint: Sprint = Sprint()

        self.tried_to_attack_while_hookax_push: bool = False

    def __str__(self) -> str:
        return super().__str__()+'.player'

#
    def animationAction(self) -> None:
        '''Sets actions for the player according to the current animation stage.\n'''
        super().animationAction()

        if not self.isMoving(): Player.footstep_sound.stop()

        if self.stats.is_taking_damage and Player.hurt_sound.get_num_channels() == 0:
            Player.hurt_sound.play()

        if self.action == 1: # attacking
            self.current_attack.damage = 1

            if int(self.animator.index_image) in [9,12,16]:
                # attack sound.
                if Player.hit_sound.get_num_channels() == 0: Player.hit_sound.play()

                self.current_attack.damage = 140

                # attack movement.
                self.complementSpeed(self.speed_dir*self.speed_value*4)
                    
            elif Player.hit_sound.get_num_channels() > 0: Player.hit_sound.stop()

            return

        if self.action == 2: # defending
            return       

        if self.action == 3: # casting
            self.animator.setEAP(lambda: self.launchMeteor())
            return
        
        if self.action == 4: # sliding
            self.complementSpeed(self.slide_speed)
            self.animator.setEAP(lambda: self.resetCombat())
            return
        
        if self.isMoving() and Player.footstep_sound.get_num_channels() == 0: 
            Player.footstep_sound.play()
            return

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()

        self.animator.changeUpdateCoeficient( self.animator.upd_coeficient + self.stats.getPercentage(3)*7 )

        if self.action == -1:
            self.animator.setRange( (43,54) )
            return
        
        if self.action == -2:
            self.animator.setRange( (23,26) )
            if self.hookax.pushing: self.animator.resizeRange(2,3)
            self.animator.setEAP( lambda: self.endPullingAnimation() )
            return
        
        if self.stats.is_taking_damage:
            self.animator.setRange( (90,93) )
            self.animator.resizeRange(2,3)
            return

        if self.action == 1:
            self.animator.setRange( (6,22) )
            self.animator.setEAP( lambda: self.resetCombat() )
            return

        if self.action == 2:
            self.animator.setRange( (65,68) )
            self.animator.resizeRange(2,3)
            return

        if self.action == 3:
            self.animator.setRange( (54,62) )
            return

        if self.action == 4:
            self.animator.setRange( (78,86) )
            return

        if self.isMoving():
            self.animator.setRange( (38,42) )
            return
        
        #idle animation.
        self.animator.setRange( (0,5) )
#

    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Player movement gets faster while the player is running.\n'''
        if self.speed_dir == pg.math.Vector2(0,0) or self.getLockMovement(): return super().getMovementSpeed()

        self.stats.spend(Entity.dt, .25, 3)
        return self.speed_dir.normalize()*self.speed_boost*self.stats.getPercentage(3)*Entity.dt + super().getMovementSpeed()
    
    def checkInputs(self, events: list[ent.pg.event.Event]) -> None:
        '''Check keyboard and mouse inputs.\n'''

        for ev in events:

            if ev.type == ent.pg.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    self.attack()

                elif ev.button == 3:
                    self.defend()

            if ev.type == ent.pg.MOUSEBUTTONUP:
                if ev.button == 1:
                    self.resetCombat()
                
                elif ev.button == 3:
                    self.resetCombat()

            if ev.type == ent.pg.KEYDOWN:
                
                if ev.key == 119: #ord('w')
                    self.speed_dir[1] -= 1

                elif ev.key == 115: #ord('s')
                    self.speed_dir[1] += 1

                elif ev.key == 97: #ord('a')
                    self.speed_dir[0] -= 1

                elif ev.key == 100: #ord('d')
                    self.speed_dir[0] += 1

                elif ev.key == 116: #ord('t')
                    self.cast()

                elif ev.key == 114: #ord('r')
                    self.launchHookax()

                elif ev.key == ent.pg.K_SPACE:
                    self.slide()

                elif ev.key == pg.K_LSHIFT:
                    self.sprint()
            
            if ev.type == ent.pg.KEYUP:
                
                if ev.key == 119: #ord('w')
                    self.speed_dir[1] += 1

                elif ev.key == 115: #ord('s')
                    self.speed_dir[1] -= 1

                elif ev.key == 97: #ord('a')
                    self.speed_dir[0] += 1

                elif ev.key == 100: #ord('d')
                    self.speed_dir[0] -= 1

                elif ev.key == 116: #ord('e')
                    self.resetCombat()

#            
    def endPullingAnimation(self) -> None:
        super().resetAction()

        if self.tried_to_attack_while_hookax_push:
            self.tried_to_attack_while_hookax_push = False
            self.attack()

    def attack(self) -> None:
        '''Toogles player's attack, if possible.\n'''

        if self.hookax != None and self.hookax.pushing: 
            self.tried_to_attack_while_hookax_push = True

        if (self.action == 0 and not self.stats.is_taking_damage and self.attacks[0].canUse(self.stats)):
            self.action = 1
            self.current_attack = self.attacks[0]        

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

            if self.speed_dir == ent.pg.math.Vector2(0,0): self.slide_speed = self.speed_dir

            else: self.slide_speed = self.speed_dir.normalize()*self.speed_value*2.3
#

    def setCurrentAttack(self, attack: ent.Attack) -> bool:
        '''If the attack can be used, sets it as current attack, applies it's cost and returns True.\n
           If attack can't be used, returns false.\n
           Sets the instance action with (index+1). Where the index represents the position of the attack in the list.\n'''
        if attack.canUse(self.stats):
            self.current_attack = attack
            self.action = self.attacks.index(self.current_attack)+1

            self.useMana(attack.mana_cost, True)
            self.useStamina(attack.stamina_cost, True)

            return True
        
        return False

#
    def getLifeSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,10)

    def getManaSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,21)

    def getStaminaSurfacePos(self) -> ent.pg.math.Vector2:
        return ent.pg.math.Vector2(5,28)
#

    def blitStats(self) -> None:
        '''Blits player stats.\n
           Life+Mana+Stamina.\n'''

        ent.Entity.blitter.addImage(ent.Entity.blitter.lastLayer(),
                                    self.stats.getStatSurface(1, 10),
                                    self.getLifeSurfacePos())

        ent.Entity.blitter.addImage(ent.Entity.blitter.lastLayer(), 
                                    self.stats.getStatSurface(2,8),
                                    self.getManaSurfacePos())

        ent.Entity.blitter.addImage(ent.Entity.blitter.lastLayer(), 
                                    self.stats.getStatSurface(3,8),
                                    self.getStaminaSurfacePos())

    def damageSelf(self, attack: ent.Attack) -> None:
        '''Almost the same as the entity's procedure.\n
           If defending inflicts reduced damage to life, but damages stamina.\n'''
        
        if self.action == 2: # defending.
            attack.damage = attack.damage*0.2
            self.stats.spend(ent.Entity.dt, attack.damage*0.6, 3)
            return

        super().damageSelf(attack)

    def update(self, events: list[ent.pg.event.Event]) -> None:
        self.meteor.update()
        self.Sprint.update(events)

        if self.hookax != None: self.hookax.update(events)
        
        super().update()

        if self.is_dead: return

        self.checkInputs(events)
        self.animationAction()

# power methods.
    def sprint(self) -> None:
        self.Sprint.use()

    def launchHookax(self) -> None:
        if self.hookax == None: return

        if self.hookax.active: 
            self.cast()
            return
        
        self.hookax.use()

    def launchMeteor(self) -> None:
        self.meteor.use()
        self.resetCombat()

# data saving and loading.
    def __del__(self) -> None:
        playerDict = {
            'x': self.pos[0],
            'y': self.pos[1]
        }

        entInfos: dict = {}

        with open('infos/game.json', 'r') as file:
            entInfos = ent.load(file)
            entInfos[Player.infoCode()] = playerDict

        with open('infos/game.json', 'w') as file:
            file.write( ent.dumps(entInfos, indent=2) )
    
Player.handleJson()