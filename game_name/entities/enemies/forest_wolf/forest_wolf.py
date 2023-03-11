from game_name.entities.enemies.enemy import *
from io import open
from random import choices

spritesheet = ['assets/entities/enemies/forestwolf/forestwolf96x96.png']

class ForestWolf(Enemy):
    
    def __init__(self, pos: ent.pg.math.Vector2, layer: int=1, speed_value: float=90, max_life: float=80, max_mana: float=0, max_stamina: float=200) -> None:
        super().__init__(pos, layer, speed_value, max_life, max_mana, max_stamina)
        self.animator: ent.an.Animator = ent.an.Animator(ent.pg.image.load(spritesheet[0]).convert_alpha(),
                                                         [96,96],
                                                         [4,6,6,6,6,6,4,4,6])
        self.rect_adjust = (-50,-40)

        self.seek_player_interval = (0,70)
        self.random_move_interval = (70,100)
        self.distance_player_interval = (None,None)
        self.idle_interval = (None,None)

        self.upd_mov_behavior_coeficient = 4

        self.attacks: list[ent.Attack] = [ent.Attack(stamina_cost=20, range=50),
                                          ent.Attack(stamina_cost=20, range=20),
                                          ent.Attack(stamina_cost=70, range=150, knockback=ent.pg.math.Vector2(5,5))]
        self.attack_prob: list[float] = [.4,.4,.2]                  

        self.stats.setRegenFactor(2, 1)
        self.stats.setRegenFactor(0, 2)
        self.stats.setRegenFactor(6, 3)

        self.default_speed_value: float = self.speed_value
        self.stamina_run_cost: float = 4
        self.speed_booster: float = 95
        
    def __str__(self) -> str:
        return super().__str__()+'forest_wolf'
    
    def setLookingDir(self) -> bool:
        '''The sprites of this entity are horizontally inverted in the png.\n
           This function works exactly the opposite of the entity's function.\n'''
        if self.speed_dir[0] > 0: self.isLookingRight = False
        elif self.speed_dir[0] < 0: self.isLookingRight = True

#
    def activate(self) -> None:
        self.alert_distance_squared = 700**2
        return super().activate()
    
    def deactivate(self) -> None:
        self.alert_distance_squared = 225**2
        return super().deactivate()
#

#
    def setHitbox(self) -> None:
        '''Sets the damage infliction rect of the forest wolf according to it's action.\n
           Has special hitbox only for the idle bit attacks.\n'''
        super().setHitbox()
        
        if self.action in [1,2]:
            if self.isLookingRight: self.damage_rect = ent.pg.rect.Rect( ent.pg.math.Vector2(self.rect.topleft)+ent.pg.math.Vector2(45,30),
                                                                         (40,20) )
                
            else: self.damage_rect = ent.pg.rect.Rect( ent.pg.math.Vector2(self.rect.topleft)+ent.pg.math.Vector2(-20,30),
                                                      (40,20) )    

    def controlCombat(self) -> None:
        '''Controls the water_priestess attack.\n'''

        # alredy taking action.
        if self.action != 0: return
        if self.stats.is_taking_damage: return
        
        attack_choosed = choices(self.attacks, self.attack_prob, k=1)[0]
        self.setCurrentAttack(attack_choosed)

    def animationAction(self) -> None:
        '''Controls water_priestess animation behavior.\n'''
        super().animationAction()
        percentage = self.animator.animationPercentage()

        if self.action == 1:
            if percentage > 0.8: self.current_attack.damage = 40
            
            return
        
        if self.action == 2:
            if percentage > 0.8: self.current_attack.damage = 40
            
            return

        if self.action == 3:
            if ent.inInterval((.3,.6), percentage) : 
                self.complementSpeed( self.speed_dir*self.speed_value*5 )
                self.current_attack.damage = 200
            return

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange( (42,47) )
            return

        if self.stats.is_taking_damage:
            self.animator.setRange( (38,42) )
            return

        if self.action == 1: # attack 1.
            self.animator.setRange( (10,16) )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 2: # attack 2.
            self.animator.setRange( (16,22) )
            self.animator.setEAP( lambda: self.resetCombat() )
            return
        
        if self.action == 3: # attack 3(running).
            self.animator.setRange( (28,34) )
            self.animator.setEAP( lambda: self.resetCombat() )
            return

        if self.isMoving():
            self.animator.setRange( (22,28) )
            self.animator.resizeRange( 3,6 )
            return

    def setSeekPlayerSpeed(self) -> None:
        '''Forest Wolf seek player function.\n
           This enemy focus on the player, goes with everthing, than stops seeking player for stamina recovering.\n
           Enemy consumes stamina while seeking the player.\n'''        
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

        return instances