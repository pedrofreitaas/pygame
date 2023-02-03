import game_name.entities.enemies.enemy as en

spritesheet_path = ['assets/entities/enemies/waterpriestess/waterpriestess288x128.png']

class WaterPriestess(en.Enemy):
    def __init__(self, pos: en.ent.pg.math.Vector2, layer: int, speed_value: float=100) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator = en.ent.an.Animator(en.ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                           [288,128], [8,10,8,3,3,8,6,7,21,27,32,12,12,7,16])

    def update(self) -> None:
        return super().update()