from game_name.entities.enemies.enemy import *
from io import open
from random import choices

spritesheet_path = ['assets/entities/enemies/ronin/ronin.png']

class Ronin( Enemy ):

    def __init__(self, pos: ent.pg.math.Vector2) -> None:
        super().__init__(pos, 1, speed_value=90, max_life=150, max_mana=80, max_stamina=160)
        
        self.loadSprites()
        self.stats_blit_adjust: ent.pg.math.Vector2 = ent.pg.math.Vector2(0,-20)

        self.attacks.append(ent.Attack(damage=60, mana_cost=40, range=70))

        self.stats.setRegenFactor(5, 2)
        
    def loadSprites(self) -> None:
        '''Loads ronin's animations.\n'''

        self.animator = ent.an.Animator( ent.pg.image.load(spritesheet_path[0]).convert_alpha(),
                                        (128,96),
                                        (12,12,12,12,12,12,12,12,4))
                
        self.animations_range: dict[str, tuple[int,int]] = {'attack': (0,26),
                                                            'death': (27,43),
                                                            'take_dmg': (44,51),
                                                            'jump': (52,68),
                                                            'dash': (69,80),
                                                            'run': (81,93),
                                                            'idle': (94,self.animator.getTotalImages())}

    def controlCombat(self) -> None:
        if self.action != 0: return
        if self.stats.is_taking_damage: return

        self.setCurrentAttack(self.attacks[0])

    def controlAnimator(self) -> None:
        super().controlAnimator()
        super().animationAction()

        self.animator.changeUpdateCoeficient( 8 )

        if self.action == -1:
            self.animator.setRange( self.animations_range['death'] )
            return
        
        if self.stats.is_taking_damage:
            self.animator.setRange( self.animations_range['take_dmg'] )
            return

        if self.action == 1:
            self.animator.changeUpdateCoeficient( 12 )
            self.animator.setRange( self.animations_range['attack'] )
            self.animator.setEAP( lambda: self.resetCombat() )
            return

        if self.isMoving():
            self.animator.setRange( self.animations_range['run'] )
            self.animator.resizeRange( 4,6 ) 
            return
        
        self.animator.setRange( self.animations_range['idle'] )

def handleJson() -> list[Ronin]:
    '''Creates instances of Ronin based in the content of the json file.\n
       Json syntax:\n
       "ronin": {\n
            "quantity": N,\n
            "x": [x1, x2, x3, ..., xN],\n
            "y": [y1, y2, y3, ..., yN]\n
       }\n'''
    with open('infos/game.json', 'r') as file:
        entInfos = ent.load(file)

        if 'ronin' not in entInfos:
            return []
        
        instances = []
        for i in range(entInfos['ronin']['quantity']):
            instances.append( Ronin(ent.pg.math.Vector2(entInfos['ronin']['x'][i], entInfos['ronin']['y'][i])) )
        
        return instances