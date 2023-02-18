import game_name.entities.entity as ent

class Power(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value,0,0,0)

        self.active = False

    def activate(self) -> None:
        '''Power general activation.\n'''
        if not self.active: ent.unpauseTimers(self.timers)
        self.active = True

    def deactivate(self) -> None:
        '''Power general deactivation.\n'''
        if self.active: ent.pauseTimers(self.timers)
        self.active = False

    def update(self) -> None:
        '''Regular power update, only updates if the instance is active.\n'''
        if not self.active:
            return
        
        return super().update()