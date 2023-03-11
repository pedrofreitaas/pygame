from game_name.entities.entity import *
from game_name.entities.combat import *

class Power(Entity):
    def __init__(self, layer: int, speed_value: float, caster_stats: Stats, damage: float, mana_cost: float=0, range: float=0, stamina_cost: float=0, instant: bool=False, cooldown: float=0, effect: Effect=None) -> None:
        '''The power's and caster's stats are shared.\n
           Remember to call initialize method at the of subclass __init__() methods.\n'''
        Entity.__init__(self, pg.math.Vector2(0,0), layer, speed_value, 1,0,0)
        
        self.current_attack: Attack = Attack(damage=damage, mana_cost=mana_cost, stamina_cost=stamina_cost, effect=effect, instant=instant, range=range)
        self.attacks.append(self.current_attack)

        self.stats: Stats = caster_stats
        self.in_cooldown: bool = False
        self.cooldown_timer: Timer = Timer(cooldown, lambda: self.setOutOfCooldown(), -1)

    def __str__(self) -> str:
        return super().__str__()+'.power'

    def initialize(self) -> None:
        '''Prepares the power for it's first utilization.\n'''
        self.deactivate()
        self.setOutOfCooldown()

#
    def setOutOfCooldown(self) -> None:
        '''Sets the instance out of cooldown.\n'''
        if not self.in_cooldown: return
        self.in_cooldown = False
        print('Out of cooldown: ' + self.__str__())

    def setInCooldown(self) -> None:
        '''Sets the instance in cooldown.\n'''
        if self.in_cooldown: return
        self.in_cooldown = True
        self.cooldown_timer.restart()
        print('Set in cooldown: ' + self.__str__())
#

    def damageSelf(self, attack: Attack) -> None:
        '''By default powers don't take damage.\n'''

#
    def canUse(self, distance_to_target_squared: float=0) -> bool:
        return self.current_attack.canUse(self.stats, distance_to_target_squared) and not self.in_cooldown and not self.active
    
    def use(self, distance_to_target_squared: float=0) -> bool:
        '''Checks if attack can be used and uses it, returns true if so.\n
           The vector parameters are used to calculate the distance between user can target, to be compared with the power's attack's range.\n
           Applies the mana/stamina costs.\n
           Do nothing if power is in use.\n'''
        if not self.canUse(distance_to_target_squared): return False
        
        self.stats.spend(1, self.current_attack.mana_cost, 2)
        self.stats.spend(1, self.current_attack.stamina_cost, 3)

        self.activate()

        return True
#

#
    def activate(self) -> None:
        self.cooldown_timer.deactiveTimer()
        return super().activate()

    def deactivate(self) -> None:
        '''Sets power in cooldown.\n'''
        self.setInCooldown()
        self.cooldown_timer.activateTimer()
        return super().deactivate()
#

    def activeAndNotActiveBlitting(self) -> None:
        '''Blits even if the power isn't activated.\n'''

    def update(self) -> None:
        '''Also updates the cooldown timer.\n
           Does nothing if deactivated.\n'''
        updateTimers([self.cooldown_timer])
        self.activeAndNotActiveBlitting()
        if not self.active: return
        return super().update()

def updatePowers(powers: list[Power]) -> None:
    for power in powers: power.update()
