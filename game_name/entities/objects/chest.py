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
                                    (5,5),
                                    (48,32) )

Chest.handleJson()