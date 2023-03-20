from game_name.entities.enemies.enemy import *
from io import open
from game_name.entities.enemies.earth_monk.bulldoze import *
from random import choices

spritesheet_path = ['assets/entities/enemies/earthmonk/earthmonk288x128.png']

class EarthMonk( Enemy ):

#
    def infoCode() -> str:
        return Enemy.infoCode()+'.earth_monk'
#

    def __init__(self, pos: ent.pg.math.Vector2) -> None:
        super().__init__(pos, 1, 60, 160, 120, 60)
        
        self.animaton_ranges: dict[tuple[int,int]]
        self.loadSprites()

        self.rect_adjust: tuple[int,int] = (-260,-80)

        self.seek_player_interval = (0,70)
        self.random_move_interval = (70,85)
        self.distance_player_interval = (85,95)
        self.idle_interval = (95,100)

        self.attacks.extend( (ent.Attack(damage=30, mana_cost=20, range=30), #punch1
                              ent.Attack(damage=30, mana_cost=20, range=40), #punch2
                              ent.Attack(damage=35, mana_cost=30, range=40), #punch3
                              ent.Attack(damage=50, mana_cost=10, stamina_cost=40, range=90), #round kick
                              ent.Attack(damage=10, mana_cost=50, stamina_cost=50,range=45, effect=None) ) ) #earth hand
        
        self.attack_prob: tuple[float] = (.25,.25,.25,.145,.105)

        self.stats.setRegenFactor(1.2, 1)
        self.stats.setRegenFactor(4, 2)
        self.stats.setRegenFactor(7, 3)

        #powers
        self.bulldoze: Bulldoze = Bulldoze(self.stats)

    def loadSprites(self) -> None:
        '''Loads entity's sprites.\n'''

        self.animator = ent.an.Animator( ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                        (288,128),
                                        (6,8,3,3,7,6,12,23,25,16,6,13,6,15) )
                                        
        
        self.animaton_ranges: dict[tuple[int,int]] = {'idle': (0,6),
                                                      'run': (6,14),
                                                      'rise': (14,17),
                                                      'fall': (17,20),
                                                      'round_kick': (20,27),
                                                      'punch1': (27,33),
                                                      'punch2': (33,45),
                                                      'punch3': (45,68),
                                                      'earth_hand': (68,93),
                                                      'meditate': (93,109),
                                                      'roll': (109,115),
                                                      'block': (115,128),
                                                      'take_dmg': (128,134),
                                                      'death': (134,149) }

    def __str__(self) -> str:
        return EarthMonk.infoCode()

#   
    def activate(self) -> None:
        self.alert_distance_squared = 600**2
        return super().activate()
    
    def deactivate(self) -> None:
        self.alert_distance_squared = 200**2
        return super().deactivate()
#

    def defend(self) -> None:
        if self.action != 0: return
        if self.stats.is_taking_damage: return
        if ent.Entity.player.action <= 0: return

        self.action = 6

#
    def controlCombat(self) -> None:
        if self.action != 0: return
        if self.stats.is_taking_damage: return

        if self.randomizer.randint(0,1000) < 250: return

        if self.bulldoze.canUse(self.distance_to_player_squared):
            self.action = 7
            return

        if self.stats.hasEnough(10,3) and self.randomizer.randint(0,1000) < 2:
            self.defend()
            return
        
        if self.randomizer.randint(0,1000) > 800: return

        self.setCurrentAttack( choices(self.attacks, self.attack_prob, k=1)[0] )
#

    def setHitbox(self) -> None:
        super().setHitbox()

        if self.action in (1,2): 
            self.damage_rect.inflate_ip((0,-20))

            if self.isLookingRight: self.damage_rect.move_ip((30,0))
            else: self.damage_rect.move_ip((-30,0))

            return
        
        if self.action == 3:
            
            if self.isLookingRight: self.damage_rect.move_ip((30+40*self.animator.animationPercentage(),0))
            else: self.damage_rect.move_ip((-30-40*self.animator.animationPercentage(),0))
            
            return

        if self.action == 4: 
            self.damage_rect.inflate_ip(30, -10)
            return
        
        if self.action == 5: 
            self.damage_rect.inflate_ip(30,0)

            if self.isLookingRight: self.damage_rect.move_ip((35,0))
            else: self.damage_rect.move_ip((-40,0))
            
            return

    def damageSelf(self, attack: ent.Attack) -> None:
        '''Reduces damage and spend stamina in case the earth monk is blocking.\n'''

        if self.action == 6 and self.stats.spend(ent.Entity.dt, 6, 3): attack.damage *= 0.3
    
        return super().damageSelf(attack)

#
    def animationAction(self) -> None:
        super().animationAction()

        percentage = self.animator.animationPercentage()

        if self.action == 1: 
            self.animator.changeUpdateCoeficient(12)
            return

        if self.action == 2:
            self.animator.changeUpdateCoeficient(12)
            return

        if self.action == 3:
            self.animator.changeUpdateCoeficient(12) 
            if percentage > .7: self.current_attack.knockback = self.speed_dir*self.speed_value*4
            return

        if self.action == 4:
            if not ent.inInterval((.3,.6),percentage): return
            self.complementSpeed( self.speed_dir * self.speed_value * 4 )
            return

        if self.action == 5: 
            if not ent.inInterval((.2,.3), percentage): self.current_attack.effect = None
            else: self.current_attack.effect = ent.Stun(1.8)

            return

        if self.action == 6:
            if not self.stats.hasEnough(5, 3) or self.randomizer.randint(0,1000) < 2: self.resetCombat()
            return

        if self.action == 7:
            if percentage > .4: self.animator.changeUpdateCoeficient( self.animator.upd_coeficient*.5)
            return

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange(self.animaton_ranges['death'])
            return
        
        if self.stats.is_taking_damage:
            self.animator.setRange( self.animaton_ranges['take_dmg'] )
            return
        
        if self.action == 1:
            self.animator.setRange( self.animaton_ranges['punch1'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return

        if self.action == 2:
            self.animator.setRange( self.animaton_ranges['punch2'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 3:
            self.animator.setRange( self.animaton_ranges['punch3'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 4:
            self.animator.setRange( self.animaton_ranges['round_kick'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 5:
            self.animator.setRange( self.animaton_ranges['earth_hand'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 6:
            self.animator.setRange( self.animaton_ranges['block'] )
            self.animator.resizeRange(4,9)
            return
        
        if self.action == 7:
            self.animator.setRange( self.animaton_ranges['meditate'] )
            self.animator.setEAP(lambda: self.launchBulldoze())
            return
        
        if self.isMoving():
            self.animator.setRange( self.animaton_ranges['run'] )
            return

        self.animator.setRange( self.animaton_ranges['idle'] )

    def launchBulldoze(self) -> None:
        '''Launches bulldoze attack.\n'''
        self.bulldoze.use(self.center(), self.distance_to_player_squared)
        self.resetAction()

    def update(self) -> None:
        self.bulldoze.update()
        return super().update()

EarthMonk.handleJson()
