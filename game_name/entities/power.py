import game_name.entities.entity as ent

class Power(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.activated = False

    def activate(self) -> None:
        '''Power general activation.\n'''
        self.activated = True

    def deactive(self) -> None:
        '''Power general deactivation.\n'''
        self.activated = False

    def update(self) -> None:
        '''Regular power update, only updates if the instance is activated.\n'''
        if not self.activated:
            return
        
        return super().update()