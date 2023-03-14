from game_name.entities.entity import *
from io import open

class Object(Entity):
    '''Entity that isn't alive:\n
       -> Doesn't move.\n
       -> Doesn't take damage.\n
       -> Doesn't have stats.\n
       -> Can have animations, timers...\n'''

    def __init__(self, pos: pg.math.Vector2, layer: int) -> None:
        super().__init__(pos, layer, 0, 0, 0, 0)

    def __str__(self) -> str:
        return super().__str__()+'.object'

    def getMovementSpeed(self) -> pg.math.Vector2:
        return pg.math.Vector2(0,0)

    def move(self) -> None:
        '''Objects don't move.\n'''

    def __del__(self) -> None:
        dict = {
            'x': self.pos[0],
            'y': self.pos[1]
        }

        entInfos: dict = {}

        with open('infos/game.json', 'r') as file:
            entInfos = load(file)
            entInfos[self.__str__()] = dict

        with open('infos/game.json', 'w') as file:
            file.write( dumps(entInfos, indent=2) )


class Chest(Object):
    def __init__(self, pos: pg.math.Vector2) -> None:
        super().__init__(pos, Entity.player.layer)

    