import game_name.entities.enemies.enemy as en

spritesheet_path = ['assets/entities/enemies/waterpriestess/waterpriestess288x128.png']

class WaterPriestess(en.Enemy):
    def __init__(self, pos: en.ent.pg.math.Vector2, layer: int, speed_value: float=100) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator = en.ent.an.Animator(en.ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                           [288,128], [8,10,8,3,3,8,6,7,21,27,32,12,12,7,16])
        
        self.rect_adjust = [-250,-85]

        self.random_move_interval = [0,30]
        self.seek_player_interval = [30,80]
        self.distance_player_interval = [80,85]
        self.idle_interval = [85,100]

    def controlAnimator(self) -> None:
        super().controlAnimator()
        
        if self.isMoving():
            self.animator.setRange([15,23])
            self.animator.activateStopAtEnd()
            return
        

        self.animator.setRange([0,7])