from game_name.entities.enemies.enemy import *
from io import open
from random import choices

spritesheet_path = ['assets/entities/enemies/earthmonk/earthmonk288x128.png']

class EarthMonk( Enemy ):

    def __init__(self, pos: ent.pg.math.Vector2) -> None:
        super().__init__(pos, 1, 60, 160, 120, 60)
        
        self.animaton_ranges: dict[tuple[int,int]]
        self.loadSprites()

        self.rect_adjust: tuple[int,int] = (-260,-80)

        self.seek_player_interval = (0,70)
        self.random_move_interval = (70,85)
        self.distance_player_interval = (85,95)
        self.idle_interval = (95,100)

    def loadSprites(self) -> None:
        '''Loads entity's sprites.\n'''

        self.animator = ent.an.Animator( ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                        (288,128),
                                        (6,8,3,3,7,6,12,23,25,16,6,13,6,15) )
                                        
        
        self.animaton_ranges: dict[tuple[int,int]] = {'idle': (0,6),
                                                      'run': (6,14),
                                                      'rise': (14,17),
                                                      'fall': (17,20),
                                                      'round_kick': (20,27),
                                                      'punch1': (27,33),
                                                      'punch2': (33,45),
                                                      'punch3': (45,68),
                                                      'earth_hand': (68,93),
                                                      'meditate': (93,109),
                                                      'roll': (109,115),
                                                      'block': (115,128),
                                                      'take_dmg': (128,134),
                                                      'death': (134,149) }

#   
    def activate(self) -> None:
        self.alert_distance_squared = 600**2
        return super().activate()
    
    def deactivate(self) -> None:
        self.alert_distance_squared = 200**2
        return super().deactivate()
#

#
    def animationAction(self) -> None:
        return super().animationAction()

    def controlAnimator(self) -> None:
        super().controlAnimator()
        self.animationAction()

        if self.action == -1:
            self.animator.setRange(self.animaton_ranges['death'])
            return
        
        if self.stats.is_taking_damage:
            self.animator.setRange( self.animaton_ranges['take_dmg'] )
            return

        if self.isMoving():
            self.animator.setRange( self.animaton_ranges['run'] )
            return

        self.animator.setRange( self.animaton_ranges['idle'] )
#

    def blit(self) -> None:
        ent.Entity.blitter.addRect(2, self.rect, (255,0,0), 2)
        ent.Entity.blitter.addRect(2, self.damage_rect, (0,0,255), 2)
        return super().blit()

def handleJson() -> list[EarthMonk]:
    '''Creates instances of EarthMonk based in the content of the json file.\n
       Json syntax:\n
       "earth_monk": {\n
            "quantity": N,\n
            "x": [x1, x2, x3, ..., xN],\n
            "y": [y1, y2, y3, ..., yN]\n
       }\n'''
    with open('infos/game.json', 'r') as file:
        entInfos = ent.load(file)

        if 'earth_monk' not in entInfos:
            return []
        
        instances = []
        for i in range(entInfos['earth_monk']['quantity']):
            instances.append( EarthMonk(ent.pg.math.Vector2(entInfos['earth_monk']['x'][i], entInfos['earth_monk']['y'][i])) )

        return instances
