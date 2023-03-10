from timer import *
import pygame as pg
from game_name.entities.stats import * 

class Effect():
    def __init__(self, time: float=0) -> None:
        self.time: float = time

class Stun(Effect):
    def __init__(self, time: float) -> None:
        super().__init__(time)

class Paralyze(Effect):
    def __init__(self) -> None:
        super().__init__()

class Freeze(Effect):
    def __init__(self) -> None:
        super().__init__()

class Attack():
    def __init__(self, damage: float=0, instant: bool=False, mana_cost: float=0, stamina_cost: float=0, knockback: pg.math.Vector2=pg.math.Vector2(0,0), range: float=0, effect: Effect=None) -> None:
        '''Stores the infos of an attack.\n
           Damage-> represents the damage of the attack on target's life.\n
           instant-> If it's true, the damage will be applied all at once.\n
           mana_cost-> represents the mana cost of the attack.\n
           stamina_cost-> represents the stamina cost of the attack.\n
           effect-> represents the effect that will be applied to the target.\n
           OBS: 
           * if attack is based in collision, instant parameter should be false, otherwise, should be true.'''
        self.damage: float = damage

        self.instant: bool = instant
        self.mana_cost: float = mana_cost
        self.stamina_cost: float = stamina_cost

        self.effect: Effect|None = effect

        self.knockback: pg.math.Vector2 = knockback
        self.range: float = range
        self.range_squared: float = range**2

    def canUse(self, stats: Stats, userCenter: pg.math.Vector2=pg.math.Vector2(0,0), targetCenter: pg.math.Vector2=pg.math.Vector2(0,0)) -> bool:
        '''Returns true if the attack can be used.\n'''
        if not stats.hasEnough(self.mana_cost, 2): return False
        if not stats.hasEnough(self.stamina_cost, 3): return False
        if (userCenter - targetCenter).length_squared() > self.range_squared: return False

        return True