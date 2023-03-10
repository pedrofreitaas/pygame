import game_name.entities.entity as ent
import game_name.entities.player.powers.meteor as meteor
from game_name.entities.player.powers.sprint import *
from game_name.entities.player.powers.hookax import *
from io import open

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
        self.rect_adjust: tuple = [-30,-20]
        self.attacks: list[ent.Attack] = [ ent.Attack(25, stamina_cost=20) ]
        self.target: int = 1

        # player variables.
        self.slide_speed: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)
        self.setStatsSurfaces()
        self.meteor: meteor.Meteor = meteor.Meteor()
        self.hookax: Hookax = Hookax()
        self.Sprint: Sprint = Sprint()

    def __str__(self) -> str:
        return super().__str__()+'.player'

    def setStatsSurfaces(self) -> None:
        '''Sets the surface that represents the player's stats.\n'''

        self.life_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_life,10))
        self.life_surface.fill((200,0,0))

        self.mana_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_mana, 6))
        self.mana_surface.fill((0,0,180))

        self.stamina_surface: ent.pg.surface.Surface = ent.pg.surface.Surface((self.stats.max_stamina, 8))
        self.stamina_surface.fill((0,200,0))

#
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

        elif self.action == 2: # defending
            pass       

        elif self.action == 3: # casting
            self.animator.setEAP(lambda: self.launchMeteor())
        
        elif self.action == 4: # sliding
            self.complementSpeed(self.slide_speed)
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*2)
            self.animator.setEAP(lambda: self.resetCombat())
        
        if self.isMoving(): Player.footstep_sound.play()
        else: Player.footstep_sound.stop()

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()

        if self.action == -1:
            self.animator.setRange( (43,54) )
            return
        
        if self.action == -2:
            self.animator.setRange( (22,26) )
            self.animator.resizeRange(3,4)
            return

        if self.stats.is_taking_damage:
            self.animator.setRange( (90,93) )
            self.animator.resizeRange(2,3)
            return

        if self.action == 1:
            self.animator.setRange( (6,23) )
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

                elif ev.key == 101: #ord('e')
                    self.cast()

                elif ev.key == 114: #ord('r')
                    self.launchHookax()
                    self.action = 5

                elif ev.key == ent.pg.K_SPACE:
                    self.slide()

                elif ev.key == ent.pg.K_LSHIFT:
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

                elif ev.key in (101,114): #ord('e'),ord('r')
                    self.resetCombat()

#            
    def attack(self) -> None:
        '''Toogles player's attack, if possible.\n'''
        if self.action == 0 and not self.stats.is_taking_damage:
            self.action = 1
            if self.attacks[0].canUse(self.stats): self.current_attack = self.attacks[0]

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
                                           self.life_surface.subsurface((0,0), (self.stats.life, 10)),
                                           self.getLifeSurfacePos())

        ent.Entity.blitter.addImage(ent.Entity.blitter.lastLayer(), 
                                           self.mana_surface.subsurface((0,0), (self.stats.mana, 6)),
                                           self.getManaSurfacePos())

        ent.Entity.blitter.addImage(ent.Entity.blitter.lastLayer(), 
                                           self.stamina_surface.subsurface((0,0), (self.stats.stamina, 8)),
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
        self.hookax.update(events)
        
        super().update()

        if self.is_dead: return

        self.checkInputs(events)
        self.animationAction()

# power methods.
    def sprint(self) -> None:
        self.Sprint.use()

    def launchHookax(self) -> None:
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
            entInfos['player'] = playerDict

        with open('infos/game.json', 'w') as file:
            file.write( ent.dumps(entInfos, indent=2) )

def createPlayer( playerDict: dict ) -> Player:
    return Player( ent.pg.math.Vector2(playerDict['x'], playerDict['y']) )

def handleJson() -> Player:
    '''Creates the player according to json data and returns it.\n'''

    with open('infos/game.json', 'r') as file:
        entInfos: dict = ent.load(file)

        if 'player' not in entInfos.keys():
            return Player(ent.pg.math.Vector2(20,20))
        
        return createPlayer( entInfos['player'] )