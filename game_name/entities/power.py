from game_name.entities.entity import *
from game_name.entities.combat import *

class Power(Entity):
    def __init__(self, layer: int, speed_value: float, damage: float, mana_cost: float=0, stamina_cost: float=0,damage_is_instant: bool=False, cooldown: float=0, effect: Effect=None) -> None:
        '''If cooldown is equal to zero, doesn't create a timer to measure it.\n'''

        Entity.__init__(self, pg.math.Vector2(0,0), layer, speed_value, 1,0,0)
        
        self.attacks: list[Attack] = []
        
        self.in_cooldown: bool = False
        self.cooldown_timer: Timer = Timer(cooldown, lambda: self.setOutOfCooldown(), -1)

    def setOutOfCooldown(self) -> None:
        '''Sets the instance out of cooldown.\n'''
        self.in_cooldown = False
        self.cooldown_timer.deactiveTimer()
        print('no interface implemented -> meteor out of cooldown')

    def setInCooldown(self) -> None:
        '''Sets the instance out of cooldown.\n'''
        self.in_cooldown = True
        self.cooldown_timer.activateTimer()
        print('no interface implemented -> meteor in cooldown')

    def canUse(self, stats: Stats, userCenter: pg.math.Vector2=pg.math.Vector2(0,0), targetCenter: pg.math.Vector2=pg.math.Vector2(0,0)) -> bool:
        '''Returns true if power can be used.\n'''
        return self.current_attack.canUse(stats, userCenter, targetCenter) and not self.in_cooldown

    def activate(self) -> None:
        '''Attack activation plus deactivation of cooldown timer.\n'''
        self.cooldown_timer.deactiveTimer()
        super().activate()

    def deactivate(self) -> None:
        '''Attack deactivation plus activation of cooldown timer.\n'''
        self.setInCooldown()
        super().deactivate()

    def update(self) -> None:
        '''Updates the cooldown timer besides the super() update method.\n'''
        if self.active: super().update()
        updateTimers([self.cooldown_timer])

def updatePowers(powers: list[Power]) -> None:
    for power in powers: power.update()
