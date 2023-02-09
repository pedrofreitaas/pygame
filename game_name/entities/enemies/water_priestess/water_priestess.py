import game_name.entities.enemies.enemy as en

spritesheet_path = ['assets/entities/enemies/waterpriestess/waterpriestess288x128.png']

class WaterPriestess(en.Enemy):
    def __init__(self, pos: en.ent.pg.math.Vector2, layer: int, speed_value: float=100) -> None:
        super().__init__(pos, layer, speed_value, 120, 60, 70)

        self.animator = en.ent.an.Animator(en.ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                           [288,128], [8,10,8,3,3,8,6,7,21,27,32,12,12,7,16])
        
        self.rect_adjust = [-250,-85]

        self.seek_player_interval = [0,65]
        self.random_move_interval = [65,80]
        self.distance_player_interval = [80,85]
        self.idle_interval = [85,100]

        self.upd_mov_behavior_coeficient = 5

    def controlCombat(self) -> None:
        '''Controls the water_priestess attack.\n'''

        # alredy taking action.
        if self.action != 0: return

        if self.stats.is_taking_damage: return

        # if not seeking player.
        if not en.ent.inInterval(self.seek_player_interval, self.movement_behavior): return
        
        distance = self.distancePlayerSquared()
        if distance >= 10000:
            return

        attack_decider = self.randomizer.randint(1,5000)

        if attack_decider <= 5: # attack 1
            self.action = 1
            return

        if attack_decider <= 10 and distance <= 3500: # attack 5
            self.action = 5
            return

        if attack_decider <= 15 and distance <= 3000: # attack 4
            self.action = 4
            return

        if attack_decider <= 40 and distance <= 1000: # attack 3
            self.action = 3
            return

        if attack_decider <= 50 and distance <= 1000: # attack 2
            self.action = 2
            return

    def animationAction(self) -> None:
        '''Controls water_priestess animation behavior.\n'''
        super().animationAction()

        percentage = self.animator.animationPercentage()

        if self.action == 1: # attack 1
            if en.ent.inInterval([0.4, 0.5], percentage):
                self.complementSpeed(self.speed_dir*self.speed_value*10)

            if self.getMovementSpeed() != en.ent.pg.math.Vector2(): self.attack_damage = 400
            
            return
        
        if self.action == 2: # attack 2.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.125)

            if en.ent.inInterval([0.4, 0.6], percentage):
                self.complementSpeed(self.speed_dir*self.speed_value*2)

            if self.getMovementSpeed() != en.ent.pg.math.Vector2(): self.attack_damage = 70

            return

        if self.action == 3: # attack 3.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.4)
            
            if en.ent.inInterval([0.1,0.2], percentage): self.attack_damage = 5
            if en.ent.inInterval([0.3,0.45], percentage): self.attack_damage = 20
            if en.ent.inInterval([0.65,0.75], percentage): self.attack_damage = 40

            return
        
        if self.action == 4: # attack 4.               
            if percentage <= 0.2: 
                self.complementSpeed(self.speed_dir*self.speed_value*0.25)
                self.setSeekPlayerSpeed()
                self.attack_damage = 20
                
            elif en.ent.inInterval([0.65,0.8], percentage): 
                self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.6)
                self.complementSpeed(self.speed_dir*self.speed_value*0.5*-1)
                self.attack_damage = 30

            elif en.ent.inInterval([0.8,0.85], percentage): 
                self.attack_knockback = self.attack_knockback + (self.speed_dir*self.speed_value*2)
                self.attack_damage = 40

            return

        if self.action == 5: # attack 5.
            self.animator.changeUpdateCoeficient(self.animator.upd_coeficient*1.75)

            if percentage < 0.4:
                self.setSeekPlayerSpeed()

            else:
                self.attack_damage = 80 * percentage

            return

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange([162, 179])
            return

        if self.stats.is_taking_damage:
            self.animator.setRange([156, 162])
            return

        if self.action == 1:
            self.animator.setRange([32,40])
            self.animator.setEAP(lambda: self.resetAction())
            return

        if self.action == 2:
            self.animator.setRange([46,52])
            self.animator.setEAP(lambda: self.resetAction())
            return

        if self.action == 3:
            self.animator.setRange([52,72])
            self.animator.setEAP(lambda: self.resetAction())
            return

        if self.action == 4:
            self.animator.setRange([72,100])
            self.animator.setEAP(lambda: self.resetAction())
            return

        if self.action == 5:
            self.animator.setRange([100,131])
            self.animator.setEAP(lambda: self.resetAction())
            return

        if self.isMoving():
            self.animator.setRange([15,23])
            self.animator.activateStopAt(0.8)
            return

        self.animator.setRange([0,7])