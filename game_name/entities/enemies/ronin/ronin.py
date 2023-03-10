from game_name.entities.enemies.enemy import *
from io import open
from random import choices

spritesheet_path = ['assets/entities/enemies/ronin/ronin.png']

class Ronin( Enemy ):

    def __init__(self, pos: ent.pg.math.Vector2) -> None:
        super().__init__(pos, 1, speed_value=110, max_life=150, max_mana=60, max_stamina=110)

        self.alert_distance_squared: float = 80**2
        
        self.loadSprites()
        self.stats_blit_adjust: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,-20)

        self.default_speed_value: float = self.speed_value

        self.attacks.append(ent.Attack(damage=60, mana_cost=5, stamina_cost=8, range=50))

        self.stats.setRegenFactor(7, 2)
        self.stats.setRegenFactor(6, 3)

        self.seek_player_interval = (0,60)
        self.random_move_interval = (60,70)
        self.distance_player_interval = (70,90)
        self.idle_interval = (90,100)

        self.jump_cost: float = 20 #instant
        self.jump_speed: float = 3.2

        self.fade_cost: float = 12 #not instant
        
        self.rect_adjust: tuple[int,int] = (-100,-45)

    def activate(self) -> None:
        self.alert_distance_squared = 600**2
        return super().activate()
    
    def deactivate(self) -> None:
        self.alert_distance_squared = 200**2
        return super().deactivate()

    def __str__(self) -> str:
        return super().__str__()+'.ronin'
    
    def loadSprites(self) -> None:
        '''Loads ronin's animations.\n'''

        self.animator = ent.an.Animator( ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                        (128,96),
                                        (12,12,12,12,12,12,12,12,4))
                
        self.animations_range: dict[str, tuple[int,int]] = {'attack': (0,26),
                                                            'death': (27,43),
                                                            'take_dmg': (44,51),
                                                            'jump': (52,68),
                                                            'fade': (69,80),
                                                            'run': (81,93),
                                                            'idle': (94,self.animator.getTotalImages())}

    def damageSelf(self, attack: ent.Attack) -> None:
        if self.action == 3: return

        return super().damageSelf(attack)
    
    def jump(self) -> None:
        '''Makes the ronin start jumping.\n'''
        if self.action != 0: return
        if not (ent.inInterval(self.distance_player_interval, self.movement_behavior) or ent.inInterval(self.seek_player_interval, self.movement_behavior)): return
        if self.speed_dir == ent.pg.math.Vector2(0,0): return
        if self.stats.hasEnough(self.jump_cost, 3) and not self.stats.spend(1, self.jump_cost, 3): return

        self.action = 2

    def fade(self) -> None:
        '''Makes the ronin fade, avoiding attacks'''
        if self.action != 0: return
        if ent.Entity.player.action != 1: return
        if self.stats.hasEnough(self.fade_cost,3) and not self.stats.spend(1, self.fade_cost, 3): return

        self.action = 3

    def controlCombat(self) -> None:
        if self.getLockMovement(): return
        if self.stats.is_taking_damage: return

        if self.randomizer.randint(0,10000) < 50:
            self.jump()
            return
        
        if self.randomizer.randint(0,10) == 0: self.fade()

        self.setCurrentAttack(self.attacks[0])

    def setHitbox(self) -> None:
        super().setHitbox()

        if self.action == 1:
            if self.isLookingRight: self.damage_rect = ent.pg.rect.Rect( ent.pg.math.Vector2(self.rect.topleft)+ent.pg.math.Vector2(25,0),
                                                                         (20,40) )
                
            else: self.damage_rect = ent.pg.rect.Rect( ent.pg.math.Vector2(self.rect.topleft)-ent.pg.math.Vector2(15,0),
                                                      (20,40) )

    def animationAction(self) -> None:
        super().animationAction()

        percentage = self.animator.animationPercentage()

        if self.action == 1:
            if not self.stats.spend(ent.Entity.dt, 10, 2) or not self.stats.spend(ent.Entity.dt, 4, 3): self.resetCombat()

        if self.action == 2 and ent.inInterval((.1,.4), percentage):
            self.complementSpeed(self.speed_dir * self.speed_value * self.jump_speed)

        if self.action == 3:
            if not self.stats.spend(ent.Entity.dt, self.fade_cost, 2): self.resetAction()
            elif ent.Entity.player.action != 1: self.resetAction()

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        self.animator.changeUpdateCoeficient( 8 )

        if self.action == -1:
            self.animator.setRange( self.animations_range['death'] )
            return
        
        if self.stats.is_taking_damage:
            self.animator.setRange( self.animations_range['take_dmg'] )
            return

        if self.action == 1:
            self.animator.changeUpdateCoeficient( 12 )
            self.animator.setRange( self.animations_range['attack'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 2:
            self.animator.changeUpdateCoeficient( 11 )
            self.animator.setRange( self.animations_range['jump'] )
            self.animator.setEAP( lambda: self.resetAction() )
            return
        
        if self.action == 3:
            self.animator.setRange( self.animations_range['fade'] )
            return

        if self.isMoving():
            self.animator.setRange( self.animations_range['run'] )
            self.animator.resizeRange( 4,6 ) 
            return
        
        self.animator.setRange( self.animations_range['idle'] )

def handleJson() -> list[Ronin]:
    '''Creates instances of Ronin based in the content of the json file.\n
       Json syntax:\n
       "ronin": {\n
            "quantity": N,\n
            "x": [x1, x2, x3, ..., xN],\n
            "y": [y1, y2, y3, ..., yN]\n
       }\n'''
    with open('infos/game.json', 'r') as file:
        entInfos = ent.load(file)

        if 'ronin' not in entInfos:
            return []
        
        instances = []
        for i in range(entInfos['ronin']['quantity']):
            instances.append( Ronin(ent.pg.math.Vector2(entInfos['ronin']['x'][i], entInfos['ronin']['y'][i])) )
        
        return instances