import game_name.entities.entity as ent
from random import randint, SystemRandom

class Enemy(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.randomizer = SystemRandom(randint(1,1000))
        
        ent.Entity.enemies.append(self)

    def setRandomSpeed(self) -> None:
        '''Sets the enemy speed randomly.\n'''
        if self.randomizer.randint(1,10000) > 20: return

        self.speed: ent.pg.math.Vector2 = ent.pg.math.Vector2(self.randomizer.random(), self.randomizer.random())
        if self.speed != ent.pg.math.Vector2(): self.speed = self.speed.normalize()

    def update(self) -> None:
        self.setRandomSpeed()
        
        return super().update()

