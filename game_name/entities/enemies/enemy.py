import game_name.entities.entity as ent
from random import randint, SystemRandom

class Enemy(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float) -> None:
        super().__init__(pos, layer, speed_value)

        self.randomizer = SystemRandom(randint(1,1000))
        
        ent.Entity.enemies.append(self)

        self.movement_behavior: float = 0
        self.upd_mov_behavior_coeficient: float = 1

        self.random_move_interval = [0,30]
        self.seek_player_interval = [30,70]
        self.distance_player_interval = [70,90]
        self.idle_interval = [90,100]

        self.randommizer_coeficient = 5

    def updateMoveBehavior(self, coeficient: float) -> None:
        '''Updates the variable that controls the movement behavior.\n'''
        self.movement_behavior += coeficient * ent.Entity.dt

        if self.movement_behavior >= 100: self.movement_behavior = 0
        if self.movement_behavior < 0: self.movement_behavior = 0

    def controlAttack(self) -> None:
        '''Abstract function to control the enemy attack.\n'''
        return

    def controlMovement(self) -> None:
        '''Sets enemy movement, with a little bit of randness.\n'''
        if self.action != 0: return
        
        self.updateMoveBehavior(self.upd_mov_behavior_coeficient)

        if self.randomizer.randint(1,50000) <= self.randommizer_coeficient:
            self.movement_behavior = self.randomizer.random() * 100

        if ent.inInterval(self.random_move_interval, self.movement_behavior):
            self.setRandomSpeed()
            return

        if ent.inInterval(self.seek_player_interval, self.movement_behavior):
            self.setSeekPlayerSpeed()
            return

        if ent.inInterval(self.distance_player_interval, self.movement_behavior):
            self.setDistancePlayerSpeed()
            return

        if ent.inInterval(self.idle_interval, self.movement_behavior):
            self.speed_dir = ent.pg.math.Vector2()
            return

    def setRandomSpeed(self) -> None:
        '''Sets the enemy speed randomly.\n'''
        if self.randomizer.randint(1,50000) >= 80: return

        self.speed_dir: ent.pg.math.Vector2 = ent.pg.math.Vector2(self.randomizer.random()*self.randomizer.randint(-1,1), self.randomizer.random()*self.randomizer.randint(-1,1))
        if self.speed_dir != ent.pg.math.Vector2(): self.speed_dir = self.speed_dir.normalize()
    
    def setSeekPlayerSpeed(self) -> None:
        '''Sets the direction of movement to be towards the player.\n'''
        distance = ent.Entity.player.center() - self.center()
        if distance != ent.pg.math.Vector2(): self.speed_dir = distance.normalize()
        else: self.speed_dir = ent.pg.math.Vector2()

    def setDistancePlayerSpeed(self) -> None:
        '''Sets the direction of movement to run to get far away from the player.\n'''
        distance = self.center() - ent.Entity.player.center()
        if distance != ent.pg.math.Vector2(): self.speed_dir = distance.normalize()
        else: self.speed_dir = ent.pg.math.Vector2()

    def distancePlayerSquared(self) -> float:
        '''Returns the enemy's distance squared to the player.\n'''
        return (self.center() - ent.Entity.player.center()).length_squared()

    def update(self) -> None:
        self.controlMovement()
        self.controlAttack()
        
        return super().update()
