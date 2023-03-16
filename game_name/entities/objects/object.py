from game_name.entities.entity import *
from io import open

class Object(Entity):
    '''Entity that isn't alive:\n
       -> Doesn't move.\n
       -> Doesn't take damage.\n
       -> Doesn't have stats.\n
       -> Can have animations, timers...\n'''

# 
    def infoCode() -> str:
        return Entity.infoCode()+'.object'

    @classmethod
    def saveEmptyDict(cls: 'Object') -> dict:
        with open('infos/game.json', 'r') as file:
            entInfos = load(file)
 
            emptyEntDict: dict = {
                'quantity': 0,
                'x': [],
                'y': [],
            }

            with open('infos/game.json', 'r') as file: entInfos[cls.infoCode()] = emptyEntDict
            with open('infos/game.json', 'w') as file: file.write( dumps(entInfos, indent=2) )
    
    @classmethod
    def createInstanceWithDict(cls: 'Object', entInfos: dict) -> 'Object':
        
        for i in range(entInfos['quantity']):
            cls(pg.math.Vector2(entInfos['x'][i], entInfos['y'][i])) 
#

    def __init__(self, pos: pg.math.Vector2, layer: int) -> None:
        super().__init__(pos, layer, 0, 1, 0, 0)
        self.target: int = 0

        Entity.objects.append(self)

    def __str__(self) -> str:
        return Object.infoCode()

    def getMovementSpeed(self) -> pg.math.Vector2:
        return pg.math.Vector2(0,0)

    def move(self) -> None:
        '''Objects don't move.\n'''
    