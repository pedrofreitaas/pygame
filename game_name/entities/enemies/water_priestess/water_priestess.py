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

    def collisionUpdate(self) -> None:
        super().collisionUpdate()

        if self.action == 0:
            return

        if self.mask.overlap(en.ent.Entity.player.mask, en.ent.Entity.player.pos-self.pos) == None:
            return

        if self.action == 1:
            en.ent.Entity.player.damageSelf(10)
            return

        if self.action == 2:
            en.ent.Entity.player.damageSelf(10)
            return

        if self.action == 3:
            en.ent.Entity.player.damageSelf(10)
            return

        if self.action == 4:
            en.ent.Entity.player.damageSelf(10)
            return

        if self.action == 5:
            en.ent.Entity.player.damageSelf(10)
            return

    def controlCombat(self) -> None:
        '''Controls the water_priestess attack.\n'''

        # alredy taking action.
        if self.action != 0: return

        # if not seeking player.
        if not en.ent.inInterval(self.seek_player_interval, self.movement_behavior): return
        
        distance = self.distancePlayerSquared()
        if distance >= 10000:
            return

        attack_decider = self.randomizer.randint(1,5000)

        if attack_decider <= 3: # attack 1
            self.action = 1
            return

        if attack_decider <= 5 and distance <= 3500: # attack 5
            self.action = 5
            return

        if attack_decider <= 15 and distance <= 3000: # attack 4
            self.action = 4
            return

        if attack_decider <= 40 and distance <= 1000: # attack 3
            self.action = 3
            return

        if attack_decider <= 60 and distance <= 1000: # attack 2
            self.action = 2
            return

    def animationAction(self) -> None:
        '''Controls water_priestess animation behavior.\n'''
        super().animationAction()

        if self.action == 1:
            if int(self.animator.index_image) == 36:
                self.complementSpeed(self.speed_dir*self.speed_value*10*en.ent.Entity.dt)
            
            return
        
        if self.action == 2: # attack 2.
            percentage = self.animator.animationPercentage()
            if en.ent.inInterval([0.4, 0.6], percentage):
                self.complementSpeed(self.speed_dir*self.speed_value*2*en.ent.Entity.dt)

            return

        if self.action == 3: # attack 3.
            return
        
        if self.action == 4: # attack 4.
            percentage = self.animator.animationPercentage()
            if en.ent.inInterval([0.6, 0.8], percentage):
                self.complementSpeed(self.speed_dir*self.speed_value*0.125*en.ent.Entity.dt*-1)
            return

        if self.action == 5: # attack 5.
            return

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange([162, 179])
            return

        if self.stats.is_taking_damage:
            self.animator.setRange([177, 162])
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