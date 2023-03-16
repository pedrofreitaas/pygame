from game_name.entities.objects.object import *
from random import choices

spritesheets = ['assets/entities/objects/chest/Chests.png']

class Chest(Object):

#
    def infoCode() -> str:
        return Object.infoCode()+'.chest'
#

    def __init__(self, pos: pg.math.Vector2) -> None:
        super().__init__(pos, Entity.player.layer)

        self.animator = an.Animator( pg.image.load(spritesheets[0]).convert_alpha(),
                                     (48,32),
                                     (5,5) )

        self.interaction_key_ord: int = ord('c')

        self.interation_distance_squared: float = 40**2

        self.interaction_key_surf: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter(chr(self.interaction_key_ord), False) )
        
        centroid1 = pg.math.Vector2( pg.mask.from_surface(self.animator.image).centroid() )
        centroid2 = pg.math.Vector2( pg.mask.from_surface(self.interaction_key_surf).centroid() )

        self.interaction_key_surf_blit_pos: pg.math.Vector2 = self.pos + centroid1 - centroid2 - pg.math.Vector2(0, self.animator.image.get_size()[1])

    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        if self.action == 1:
            self.animator.setRange((0, 9))
            self.animator.setEAP(lambda: self.end())
            return

        if self.action == 2:
            self.animator.setRange( (8,9) )
            return

        self.animator.setRange((0,1))

    def open(self) -> None:
        if self.action != 0: return
        self.action = 1

    def end(self) -> None:
        if self.action != 1: return
        self.action = 2

    def interact(self) -> bool:
        if not super().interact(): return

        self.open()

    def blit(self) -> None:
        if self.can_interact:
            Entity.blitter.addImage(self.layer, self.interaction_key_surf, self.interaction_key_surf_blit_pos)

        return super().blit()


Chest.handleJson()