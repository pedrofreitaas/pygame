from game_name.entities.enemies.enemy import *
from io import open
from random import choices

spritesheet = ['assets/entities/enemies/forestwolf/forestwolf96x96.png']

class ForestWolf(Enemy):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int=1, speed_value: float=90, max_life: float=200, max_mana: float=10, max_stamina: float=200) -> None:
        super().__init__(pos, layer, speed_value, max_life, max_mana, max_stamina)
        self.animator: ent.an.Animator = ent.an.Animator(ent.pg.image.load(spritesheet[0]).convert_alpha(),
                                                         [96,96],
                                                         [10,10,6,6,6,10])
        self.rect_adjust = (-50,-40)

        self.seek_player_interval = (0,70)
        self.random_move_interval = (70,90)
        self.distance_player_interval = (90,100)
        self.idle_interval = (None,None)

        self.upd_mov_behavior_coeficient = 3

        self.attacks: list[ent.Attack] = [ent.Attack(stamina_cost=15, range=50),
                                          ent.Attack(stamina_cost=15, range=20)]
                                          #ent.Attack(stamina_cost=40, range=150, knockback=ent.pg.math.Vector2(5,5))]
        self.attack_prob: list[float] = [.5,.5]                  

        self.stats.setRegenFactor(self.stats.regen_factor*1.5)

        self.default_speed_value: float = self.speed_value
        self.stamina_run_cost: float = 10
        self.speed_booster: float = 80
        
    def __str__(self) -> str:
        return super().__str__()+'forest_wolf'
    
#
    def controlCombat(self) -> None:
        '''Controls the water_priestess attack.\n'''

        # alredy taking action.
        if self.action != 0: return

        if self.stats.is_taking_damage: return

        # if not seeking player.
        if not ent.inInterval(self.seek_player_interval, self.movement_behavior): return
        
        attack_choosed = choices(self.attacks, self.attack_prob, k=1)[0]
        self.setCurrentAttack(attack_choosed)

    def animationAction(self) -> None:
        '''Controls water_priestess animation behavior.\n'''
        super().animationAction()
        percentage = self.animator.animationPercentage()

        if self.action == 1:
            if percentage > 0.6: self.current_attack.damage = 80

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange( (30,36) )
            return

        if self.stats.is_taking_damage:
            self.animator.setRange( (36,46) )
            return

        if self.action == 1: # attack 1.
            self.animator.setRange( (0,9) )
            self.animator.setEAP(lambda: self.resetCombat())
            return

        if self.isMoving():
            self.animator.setRange( (18,24) )
            self.animator.resizeRange( 3,6 )
            return

    def setSeekPlayerSpeed(self) -> None:
        return super().setSeekPlayerSpeed()
        '''Forest Wolf seek player function.\n
           This enemy focus on the player, goes with everthing, than stops seeking player for stamina recovering.\n
           Enemy consumes stamina while moving.\n'''        
        if not self.stats.hasEnough(self.stamina_run_cost, 3):
            self.speed_value = self.default_speed_value
            self.movement_behavior = self.random_move_interval[0]
            return

        self.speed_value = self.default_speed_value + self.speed_booster*self.stats.getPercentage(3)
        self.useStamina(self.stamina_run_cost, False)
        return super().setSeekPlayerSpeed()
#

def handleJson() -> list[ForestWolf]:
    '''Creates instances of ForestWolf based in the content of the json file.\n
       Json syntax:\n
       "forest_wolf": {\n
            "quantity": N,\n
            "x": [x1, x2, x3, ..., xN],\n
            "y": [y1, y2, y3, ..., yN]\n
       }\n'''
    with open('infos/game.json', 'r') as file:
        entInfos = ent.load(file)

        if 'forest_wolf' not in entInfos:
            return []
        
        instances = []
        for i in range(entInfos['forest_wolf']['quantity']):
            instances.append( ForestWolf(ent.pg.math.Vector2(entInfos['forest_wolf']['x'][i], entInfos['forest_wolf']['y'][i])) )