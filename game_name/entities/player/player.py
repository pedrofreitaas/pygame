import game_name.entities.entity as ent

player_sprites_path = ['assets/entities/player/char_red_1.png', 'assets/entities/player/char_red_2.png' ]

class Player( ent.Entity ):
    
    def __init__(self, pos: ent.pg.math.Vector2, layer: int=1, speed_value: float=120) -> None:
        super().__init__(pos, layer, speed_value)

        self.animator: ent.an.Animator = ent.an.Animator( ent.pg.image.load(player_sprites_path[0]).convert_alpha(),
                                                          [56,56],
                                                          [6,8,8,8,8,4,8,4,8,3,3])

        self.animator.loadSprites( ent.pg.image.load(player_sprites_path[1]).convert_alpha(),
                                                          [56,56],
                                                          [8,2,8,4,8,8,2] )

        ent.Entity.player = self

    def animationAction(self) -> None:
        '''Sets actions for the player according to the current animation stage.\n'''

        if self.action == 1:
            self.setLockMovement(True)
            
            # moving player in mouse dir when it swifts the sword.
            if int(self.animator.index_image) in [9,12,16]:
                move_dir = (ent.pg.math.Vector2( ent.pg.mouse.get_pos() )-self.center())

                if move_dir != ent.pg.math.Vector2(): move_dir = move_dir.normalize()
                else: return

                self.pos = self.pos + (move_dir*self.speed_value*ent.Entity.dt)

            return

        if self.action == 2:
            self.setLockMovement(True)            
            return

        if self.action == 3:
            if self.animator.range_image[1] - self.animator.index_image <= 0.3:
                print('LAUNCH POWERRRRRRR!')
                self.resetAction()
            
            return

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()
        self.animationAction()

        if self.action == 1:
            self.animator.setRange([6,23])
            return

        if self.action == 2:
            self.animator.setRange([65,68])
            self.animator.activateStopAtEnd()
            return

        if self.action == 3:
            self.animator.setRange([54,62])
            return

        if self.isMoving():
            self.animator.setRange([38,42])
            return
        
        #idle animation.
        self.animator.setRange([0,5])

    def checkInputs(self, events: list[ent.pg.event.Event]) -> None:
        '''Check keyboard and mouse inputs.\n'''

        for ev in events:

            if ev.type == ent.pg.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    self.attack()

                elif ev.button == 3:
                    self.defend()

            if ev.type == ent.pg.MOUSEBUTTONUP:
                if ev.button in [1,3]:
                    self.resetAction()

            if ev.type == ent.pg.KEYDOWN:
                
                if ev.key == 119: #ord('w')
                    self.speed[1] -= self.speed_value

                elif ev.key == 115: #ord('s')
                    self.speed[1] += self.speed_value

                elif ev.key == 97: #ord('a')
                    self.speed[0] -= self.speed_value

                elif ev.key == 100: #ord('d')
                    self.speed[0] += self.speed_value

                elif ev.key == 101: #ord('e')
                    self.cast()
            
            if ev.type == ent.pg.KEYUP:
                
                if ev.key == 119: #ord('w')
                    self.speed[1] += self.speed_value

                elif ev.key == 115: #ord('s')
                    self.speed[1] -= self.speed_value

                elif ev.key == 97: #ord('a')
                    self.speed[0] += self.speed_value

                elif ev.key == 100: #ord('d')
                    self.speed[0] -= self.speed_value

                elif ev.key == 101: #ord('e')
                    self.resetAction()

    def update(self, events: list[ent.pg.event.Event]) -> None:
        self.checkInputs(events)

        super().update()
