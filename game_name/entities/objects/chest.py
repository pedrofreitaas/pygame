from game_name.entities.objects.object import *
from random import choices

spritesheets = ['assets/entities/objects/chest/Chests.png']

class Chest(Object):
    chests = []

#
    def infoCode() -> str:
        return Object.infoCode()+'.chest'
#

    def __init__(self, pos: pg.math.Vector2) -> None:
        super().__init__(pos, Entity.player.layer)

        chests = ( (5,5), (0,0,5,5), (0,0,0,0,5,5) )

        self.animator = an.Animator( pg.image.load(spritesheets[0]).convert_alpha(),
                                    choices(chests, (.33,.33,.33), k=1)[0],
                                    (48,32) )
        
        Chest.chests.append(self)

def handleJson() -> None:
    '''Creates instances of chest based in the content of the json file.\n
    Json syntax:\n
    "Chest.__str__()": {\n
        "quantity": N,\n
        "x": [x1, x2, x3, ..., xN],\n
        "y": [y1, y2, y3, ..., yN]\n
    }\n'''

    with open('infos/game.json', 'r') as file:
        entInfos = load(file)

        if Chest.infoCode() not in entInfos:
            emptyChestDict = {
                "quantity" : 0,
                "x": [],
                "y": []
            }

            with open('infos/game.json', 'r') as file: entInfos[Chest.infoCode()] = emptyChestDict
            with open('infos/game.json', 'w') as file: file.write( dumps(entInfos, indent=2) )

            return 
        
        for i in range(entInfos[Chest.infoCode()]['quantity']):
            chest = Chest(pg.math.Vector2(entInfos[Chest.infoCode()]['x'][i], entInfos[Chest.infoCode()]['y'][i]))

handleJson()