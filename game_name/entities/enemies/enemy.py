import game_name.entities.entity as ent
from random import randint, SystemRandom

class Enemy(ent.Entity):
    def __init__(self, pos: ent.pg.math.Vector2, layer: int, speed_value: float, max_life: float, max_mana: float, max_stamina: float) -> None:
        super().__init__(pos, layer, speed_value, max_life, max_mana, max_stamina)
        self.target: int = 2
        self.deactivate()

        self.alert_distance_squared: float = 400**2

        # enemy's variables.
        self.randomizer = SystemRandom(randint(1,1000))
        self.movement_behavior: float = 0
        self.upd_mov_behavior_coeficient: float = 1

        self.random_move_interval = [0,30]
        self.seek_player_interval = [30,70]
        self.distance_player_interval = [70,90]
        self.idle_interval = [90,100]

        self.randommizer_coeficient = 5

        self.stats_blit_adjust: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,0)
        
        ent.Entity.enemies.append(self)
    
    def __str__(self) -> str:
        return super().__str__()+'.enemy'

# artificial inteligence for movement.
    def updateMoveBehavior(self, coeficient: float) -> None:
        '''Updates the variable that controls the movement behavior.\n'''
        self.movement_behavior += coeficient * ent.Entity.dt

        if self.movement_behavior >= 100: self.movement_behavior = 0
        if self.movement_behavior < 0: self.movement_behavior = 0

    def setAleatoryMovementBehavior(self) -> None:
        '''Sets the enemy's movement behavior randomly.\n'''
        self.movement_behavior = self.randomizer.random() * 100

    def controlMovement(self) -> None:
        '''Sets enemy movement, with a little bit of randness.\n'''
        if self.getLockMovement(): return

        if self.isGoingOutOfBounds(): 
            self.movement_behavior = self.seek_player_interval[0]
        
        else:
            self.updateMoveBehavior(self.upd_mov_behavior_coeficient)

            if self.randomizer.randint(1,50000) <= self.randommizer_coeficient:
                self.setAleatoryMovementBehavior()

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
 
        if distance.length_squared() > 100: self.speed_dir = distance.normalize()
        else: self.speed_dir = ent.pg.math.Vector2()

    def setDistancePlayerSpeed(self) -> None:
        '''Sets the direction of movement to run to get far away from the player.\n'''
        distance = self.center() - ent.Entity.player.center()
        if distance != ent.pg.math.Vector2(): self.speed_dir = distance.normalize()
        else: self.speed_dir = ent.pg.math.Vector2()

    def distancePlayerSquared(self) -> float:
        '''Returns the enemy's distance squared to the player.\n'''
        return (self.center() - ent.Entity.player.center()).length_squared()

    def move(self) -> None:
        '''Moves the enemy if movement isn't locked.\n'''
        self.pos = self.pos + self.getMovementSpeed()

        # if self.isGoingOutOfBounds(): self.fitInDisplayBounds()

        self.fitOutOfStructures()

        # reseting variables for nxt loop.
        self.speed_complement: ent.pg.math.Vector2 = ent.pg.math.Vector2()
# ------------------------- #

# combat.
    def controlCombat(self) -> None:
        '''Abstract function to control the enemy's combat.\n'''
        return

    def setCurrentAttack(self, attack: ent.Attack) -> bool:
        '''If the attack can be used, sets it as current attack, applies it's cost and returns True.\n
           If attack can't be used, returns false.\n
           Sets the instance action with (index+1). Where the index represents the position of the attack in the list.\n'''
        if attack.canUse(self.stats, self.center(), ent.Entity.player.center()):
            self.current_attack = attack
            self.action = self.attacks.index(self.current_attack)+1

            self.useMana(attack.mana_cost, True)
            self.useStamina(attack.stamina_cost, True)

            return True
        
        return False
# ---------------- #

# blitting.
    def blitStats(self) -> None:
        '''Blits enemy's stats\n.'''
        if self.stats.life > 0:
            life_surf = self.stats.getStatSurface(1,3)
            coordinates = self.pos + ent.pg.math.Vector2(self.animator.image.get_width()/2,0) - ent.pg.math.Vector2(life_surf.get_size())*0.5 + self.stats_blit_adjust
            ent.Entity.blitter.addImage(self.layer, life_surf, coordinates)

        if self.stats.mana > 0:
            mana_surf = self.stats.getStatSurface(2,3)
            coordinates = self.pos + ent.pg.math.Vector2(self.animator.image.get_width()/2,0) - ent.pg.math.Vector2(mana_surf.get_size())*0.5 + self.stats_blit_adjust
            coordinates += ent.pg.math.Vector2(0,10)
            ent.Entity.blitter.addImage(self.layer, mana_surf, coordinates)

        if self.stats.stamina > 0:
            stamina_surf = self.stats.getStatSurface(3,3)
            coordinates = self.pos + ent.pg.math.Vector2(self.animator.image.get_width()/2,0) - ent.pg.math.Vector2(stamina_surf.get_size())*0.5 + self.stats_blit_adjust
            coordinates += ent.pg.math.Vector2(0,20)
            ent.Entity.blitter.addImage(self.layer, stamina_surf, coordinates)
# ----------------- #

    def die(self) -> None:
        '''Makes the enemy stop updating.\n'''
        
        try: ent.Entity.enemies.remove(self)
        except ValueError: pass

        return super().die()

    def update(self) -> None:
        if self.is_dead: return

        self.controlMovement()
        self.controlCombat()
        
        super().update()
