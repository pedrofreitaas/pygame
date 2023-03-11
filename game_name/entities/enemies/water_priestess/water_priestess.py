import game_name.entities.enemies.enemy as en
import game_name.entities.enemies.water_priestess.water_hurricane as waterH
from io import open
from random import choices

spritesheet_path = ['assets/entities/enemies/waterpriestess/waterpriestess288x128.png']

class WaterPriestess(en.Enemy):
    
    def __init__(self, pos: en.ent.pg.math.Vector2, layer: int=1, speed_value: float=100) -> None:
        super().__init__(pos, layer, speed_value, 120, 60, 70)

        self.animator = en.ent.an.Animator(en.ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                           [288,128], 
                                           [8,10,8,3,3,8,6,7,21,27,32,12,12,7,16])
        
        self.rect_adjust = (-250,-85)

        self.seek_player_interval = (0,70)
        self.random_move_interval = (70,80)
        self.distance_player_interval = (80,85)
        self.idle_interval = (85,100)

        self.upd_mov_behavior_coeficient = 5

        self.attacks: list[en.ent.Attack] = [en.ent.Attack(damage=110, mana_cost=30, stamina_cost=70, range=180),
                                             en.ent.Attack(damage=30, stamina_cost=40, range=60),
                                             en.ent.Attack(damage=30, stamina_cost=50, range=65),
                                             en.ent.Attack(damage=50, mana_cost=50, stamina_cost=20, range=60),
                                             en.ent.Attack(damage=80, mana_cost=50, stamina_cost=60, range=120)]

        self.water_hurricane: waterH.WaterHurricane = waterH.WaterHurricane(self.stats)

        self.attack_prob: list[float] = [.15, .30, .25, .15, .15]                 

        self.stats.setRegenFactor(2,1)
        self.stats.setRegenFactor(1.2, 2)
        self.stats.setRegenFactor(8, 3)

    def __str__(self) -> str:
        return super().__str__()+'.water_priestess'

#
    def activate(self) -> None:
        self.alert_distance_squared = 600**2
        return super().activate()
    
    def deactivate(self) -> None:
        self.alert_distance_squared = 150**2
        return super().deactivate()
#

#
    def controlCombat(self) -> None:
        '''Controls the water_priestess attack.\n'''

        # alredy taking action.
        if self.action != 0: return

        if self.stats.is_taking_damage: return

        rand = self.randomizer.randint(1,5000)

        if self.stats.getPercentage(1) < 0.75 and rand < 50: 
            self.action = 7 #block action
            return
        if rand < 30 and self.water_hurricane.canUse(self.distance_to_player_squared):
            self.action = 6 #waterH
            return
        
        attack_choosed = choices(self.attacks, self.attack_prob, k=1)[0]
        self.setCurrentAttack(attack_choosed)

    def animationAction(self) -> None:
        '''Controls water_priestess animation behavior.\n'''
        super().animationAction()

        percentage = self.animator.animationPercentage()

        if self.action == 1: # attack 1
            if en.ent.inInterval([0.4, 0.5], percentage):
                
                self.complementSpeed(self.speed_dir*self.speed_value*10)
            
            elif not en.ent.inInterval(self.seek_player_interval, self.movement_behavior): self.setSeekPlayerSpeed()
            
            return
        
        if self.action == 2: # attack 2.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.125)

            if en.ent.inInterval([0.4, 0.6], percentage):
                self.complementSpeed(self.speed_dir*self.speed_value*2)

            return

        if self.action == 3: # attack 3.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.4)

            return
        
        if self.action == 4: # attack 4.               
            if percentage <= 0.2: 
                self.complementSpeed(self.speed_dir*self.speed_value*0.25)
                self.setSeekPlayerSpeed()
                
            elif en.ent.inInterval([0.65,0.8], percentage): 
                self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.6)
                self.complementSpeed(self.speed_dir*self.speed_value*0.5*-1)

            return

        if self.action == 5: # attack 5.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.75)

            if percentage < 0.4: self.setSeekPlayerSpeed()
            return
        
        if self.action == 6: # water hurricane attack.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*0.8)
            return

        if self.action == 7: # defending.
            if self.stats.hasEnough(20, 3):
                self.stats.spend(en.ent.Entity.dt, 20, 3)
            else: self.resetCombat()
            return

    def waterHurricaneAttack(self) -> None:
        '''Triggers the water hurricane attack.\n'''
        self.water_hurricane.use(self.distance_to_player_squared)
        self.resetCombat()

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange( (162, 179) )
            return
        
        if self.action == -2:
            self.animator.setRange( (39,45) )
            self.animator.setEAP( lambda: self.resetCombat() )
            return

        if self.stats.is_taking_damage:
            self.animator.setRange( (156, 162) )
            return

        if self.action == 1:
            self.animator.setRange( (32,40) )
            self.animator.setEAP(lambda: self.resetCombat())
            return

        if self.action == 2:
            self.animator.setRange( (46,52) )
            self.animator.setEAP(lambda: self.resetCombat())
            return

        if self.action == 3:
            self.animator.setRange( (52,72) )
            self.animator.setEAP(lambda: self.resetCombat())
            return

        if self.action == 4:
            self.animator.setRange( (72,100) )
            self.animator.setEAP(lambda: self.resetCombat())
            return

        if self.action == 5:
            self.animator.setRange( (100,131) )
            self.animator.setEAP(lambda: self.resetCombat())
            return
        
        if self.action == 6:
            self.animator.setRange( (26,29) )
            self.animator.setEAP(lambda: self.waterHurricaneAttack())
            return
        
        if self.action == 7:
            self.animator.setRange( (145,154) )
            self.animator.resizeRange(5, 7)
            return

        if self.isMoving():
            self.animator.setRange( (15,26) )
            self.animator.resizeRange(8, 11)
            return

        self.animator.setRange( (0,7) )
#

    def damageSelf(self, attack: en.ent.Attack) -> None:
        if self.action == 7: #blocking
            self.stats.spend(en.ent.Entity.dt, attack.damage*0.3, 3)
            return
        
        return super().damageSelf(attack)

    def update(self) -> None:
        if self.active: self.water_hurricane.update()

        return super().update()

def handleJson() -> list[WaterPriestess]:
    '''Creates instances of WaterPristess based in the content of the json file.\n
       Json syntax:\n
       "water_priestess": {\n
            "quantity": N,\n
            "x": [x1, x2, x3, ..., xN],\n
            "y": [y1, y2, y3, ..., yN]\n
       }\n'''
    with open('infos/game.json', 'r') as file:
        entInfos = en.ent.load(file)

        if 'water_priestess' not in entInfos:
            return []
        
        instances = []
        for i in range(entInfos['water_priestess']['quantity']):
            instances.append( WaterPriestess(en.ent.pg.math.Vector2(entInfos['water_priestess']['x'][i], entInfos['water_priestess']['y'][i])) )

        return instances
