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

    def controlAnimator(self) -> None:
        '''Changes sprite animation based in the entity's behavior.\n'''

        super().controlAnimator()

        if self.isAttacking:
            self.animator.setRange([6,15])
            return

        if self.isMoving():
            self.animator.setRange([16,23])
            return
        
        #idle animation.
        self.animator.setRange([0,5])

    def checkInputs(self, events: list[ent.pg.event.Event]) -> None:
        '''Check keyboard and mouse inputs.\n'''

        for ev in events:

            if ev.type == ent.pg.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    self.isAttacking = True

            if ev.type == ent.pg.MOUSEBUTTONUP:
                if ev.button == 1:
                    self.isAttacking = False

            if ev.type == ent.pg.KEYDOWN:
                
                if ev.key == 119: #ord('w')
                    self.speed[1] -= self.speed_value

                elif ev.key == 115: #ord('s')
                    self.speed[1] += self.speed_value

                elif ev.key == 97: #ord('a')
                    self.speed[0] -= self.speed_value

                elif ev.key == 100: #ord('d')
                    self.speed[0] += self.speed_value
            
            if ev.type == ent.pg.KEYUP:
                
                if ev.key == 119: #ord('w')
                    self.speed[1] += self.speed_value

                elif ev.key == 115: #ord('s')
                    self.speed[1] -= self.speed_value

                elif ev.key == 97: #ord('a')
                    self.speed[0] += self.speed_value

                elif ev.key == 100: #ord('d')
                    self.speed[0] -= self.speed_value

    def update(self, events: list[ent.pg.event.Event]) -> None:
        
        self.checkInputs(events)

        super().update()