from game_name.entities.power import *

spritesheet = ['assets/entities/player/power/hookax.png']

class HookAxe(Power):
    def __init__(self, layer: int=2, speed_value: float=80, caster_stats: Stats=Entity.player.stats, damage: float=20, mana_cost: float = 15, stamina_cost: float = 0, damage_is_instant: bool = False, cooldown: float = 3, effect: Effect = None) -> None:
        super().__init__(layer, speed_value, caster_stats, damage, mana_cost, stamina_cost, damage_is_instant, cooldown, effect)

        self.animator = an.Animator( pg.image.load(spritesheet[0]).convert_alpha(),
                                     [44,44],
                                     [1] )
