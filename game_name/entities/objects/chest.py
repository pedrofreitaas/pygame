from game_name.entities.objects.object import *
from random import choices

#items:
from game_name.item import *
from game_name.entities.player.powers.hookax import HookaxItem
# ------------- #

itemDict: dict[str:type] = {
    '': Item,
    'item': Item,
    HookaxItem.infoCode(): HookaxItem
}

spritesheets = ['assets/entities/objects/chest/Chests.png']

class Chest(Object):
    dict_is_cleared: bool = False
#
    def infoCode() -> str:
        return Object.infoCode()+'.chest'

    @classmethod
    def saveEmptyDict(cls: 'Object') -> dict:
        with open('infos/game.json', 'r') as file:
            entInfos = load(file)

            entInfos[Chest.infoCode()] = {
                'quantity': 0,
                'x': [],
                'y': [],
                'opened': [],
                'item': []
            }

            with open('infos/game.json', 'w') as file: file.write( dumps(entInfos, indent=2) )
    
    @classmethod
    def createInstanceWithDict(cls: 'Object', chestInfo: dict) -> 'Object':
        for i in range(chestInfo['quantity']):
            cls(pg.math.Vector2( chestInfo['x'][i], chestInfo['y'][i]), chestInfo['opened'][i], chestInfo['item'][i] )

    def __del__(self) -> None:
        if not Chest.dict_is_cleared:
            Chest.saveEmptyDict()
            Chest.dict_is_cleared = True

        with open('infos/game.json', 'r') as file:
            entInfos = load(file)

            entInfos[Chest.infoCode()]['quantity'] += 1
            entInfos[Chest.infoCode()]['x'].append(self.pos[0])
            entInfos[Chest.infoCode()]['y'].append(self.pos[1])
            entInfos[Chest.infoCode()]['opened'].append(self.isOpen())
            entInfos[Chest.infoCode()]['item'].append(self.item.infoCode())

            with open('infos/game.json', 'w') as file: file.write( dumps(entInfos, indent=2) )
#

    def __str__(self) -> str:
        return Chest.infoCode()

    def __init__(self, pos: pg.math.Vector2, opened: bool=True, item_str: str='') -> None:
        super().__init__(pos, Entity.player.layer)

        chest_sprites = ( (5,5), (0,0,5,5), (0,0,0,0,5,5) )

        self.animator = an.Animator( pg.image.load(spritesheets[0]).convert_alpha(),
                                     (48,32),
                                     choices(chest_sprites, (.33,.33,.33), k=1)[0] )

        self.interaction_key_ord: int = ord('c')

        self.interation_distance_squared: float = 40**2

        self.interaction_key_surf: pg.surface.Surface = pg.transform.scale2x( keyboardIcons.getLetter(chr(self.interaction_key_ord), False) )
        
        centroid1 = pg.math.Vector2( pg.mask.from_surface(self.animator.image).centroid() )
        centroid2 = pg.math.Vector2( pg.mask.from_surface(self.interaction_key_surf).centroid() )

        self.interaction_key_surf_blit_pos: pg.math.Vector2 = self.pos + centroid1 - centroid2 - pg.math.Vector2(0, self.animator.image.get_size()[1])

        if opened: self.action = 2

        try: self.item: Item = itemDict[item_str](self)
        except KeyError: self.item: Item = Item(self)

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

    def interact(self) -> bool:
        if not super().interact(): return

        self.open()

#
    def isOpen(self) -> bool:
        '''Returns true if the chest has passed to opening animation and is open.\n'''
        return self.action==2

    def open(self) -> None:
        '''Starts the opening animation.\n'''
        if self.action != 0: return
        self.action = 1

    def end(self) -> None:
        '''Finishes the opening animation and makes the chest stay opened.\n'''
        if self.action != 1: return
        self.action = 2

        self.item.give(Entity.player)
#

    def blit(self) -> None:
        '''Blits both the chest and the interaction key interface.\n'''
        if self.can_interact and self.action == 0:
            Entity.blitter.addImage(self.layer, self.interaction_key_surf, self.interaction_key_surf_blit_pos)

        return super().blit()
    
Chest.handleJson()