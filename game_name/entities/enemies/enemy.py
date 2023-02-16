import game_name.entities.entity as ent
from random import randint, SystemRandom

class Enemy(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float, max_life: float, max_mana: float, max_stamina: float) -> None:
        super().__init__(pos, layer, speed_value, max_life, max_mana, max_stamina)

        self.randomizer = SystemRandom(randint(1,1000))
        
        ent.Entity.enemies.append(self)

        self.movement_behavior: float = 0
        self.upd_mov_behavior_coeficient: float = 1

        self.random_move_interval = [0,30]
        self.seek_player_interval = [30,70]
        self.distance_player_interval = [70,90]
        self.idle_interval = [90,100]

        self.randommizer_coeficient = 5

        self.attack_damage: float = 0
        self.attack_knockback: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)

    def updateMoveBehavior(self, coeficient: float) -> None:
        '''Updates the variable that controls the movement behavior.\n'''
        self.movement_behavior += coeficient * ent.Entity.dt

        if self.movement_behavior >= 100: self.movement_behavior = 0
        if self.movement_behavior < 0: self.movement_behavior = 0

    def controlCombat(self) -> None:
        '''Abstract function to control the enemy's combat.\n'''
        return

    def controlMovement(self) -> None:
        '''Sets enemy movement, with a little bit of randness.\n'''
        if self.action != 0: return

        if self.isGoingOutOfBounds(): 
            self.setSeekPlayerSpeed()
            return
        
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
        '''Sets the enemy speed_dir randomly.\n'''
        if self.randomizer.randint(1,50000) >= 150: return

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

    def blitStats(self) -> None:
        '''Blits enemy's stats\n.'''
        width, heigth = 80,3

        life_surf = ent.pg.surface.Surface((width*self.stats.life/self.stats.max_life, heigth))
        life_surf.fill((50,200,0))

        coordinates = self.pos + ent.pg.math.Vector2(self.animator.image.get_width()/2,0) - ent.pg.math.Vector2(life_surf.get_size())*0.5
        
        ent.Entity.blitter.addImage(self.layer, life_surf, coordinates)

    def collisionUpdate(self) -> None:
        '''Checks for collision between enemy and player.\n
           Uses mask collision.\n
           Inflicts the current value of attack_damage and attack_knockback if collide, and reset's this values.\n'''
        super().collisionUpdate()

        if self.action == 0:
            return

        if self.mask.overlap(ent.Entity.player.mask, ent.Entity.player.pos-self.pos) != None:
            ent.Entity.player.damageSelf(self.attack_damage)
            ent.Entity.player.complementSpeed(self.attack_knockback)

        self.attack_damage = 0
        self.attack_knockback: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)

    def die(self) -> None:
        '''Makes the enemy stop updating.\n'''
        
        try: ent.Entity.enemies.remove(self)
        except ValueError: pass

        return super().die()

    def move(self) -> None:
        '''Moves the enemy if movement isn't locked.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        # if self.isGoingOutOfBounds(): self.fitInDisplayBounds()

        self.fitOutOfStructures()

        # reseting variables for nxt loop.
        self.speed_complement: ent.pg.math.Vector2 = ent.pg.math.Vector2()

    def update(self) -> None:
        if self.is_dead: return

        self.controlMovement()
        self.controlCombat()
        
        return super().update()
