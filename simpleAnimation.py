from animator import *
from blitter import *

class SimpleAnimation():
    blitter: None|Blitter = None
    simpleAnimations: list['SimpleAnimation'] = []

    def __init__(self, pos: pg.math.Vector2, layer: int, spritsheet: pg.surface.Surface, spritesSize: tuple[int,int], spritesPerLine: tuple[int], animationSpeed: float, resize: None|tuple[int,int]) -> None:
        self.pos: pg.math.Vector2 = pos
        self.layer: int = layer
        
        self.animator = Animator(spritsheet, spritesSize, spritesPerLine)

        self.animation_speed: float = animationSpeed

        self.started: bool = False
        self.ended: bool = False

        if resize != None: self.animator.resizeSprites( resize )

        SimpleAnimation.simpleAnimations.append(self)

    def start(self) -> None:
        '''Starts animation.\n'''
        self.started = True

    def end(self) -> None:
        '''Ends the animation.\n'''
        self.ended = True

    def update(self, dt: float) -> None:
        if not self.started: return

        self.animator.setEAP(lambda: self.end())
        self.animator.changeUpdateCoeficient(self.animation_speed)
        self.animator.update(dt)

        if SimpleAnimation.blitter != None: SimpleAnimation.blitter.addImage(self.layer, self.animator.image, self.pos)

def updateSimpleAnimations(dt: float) -> None:
    '''Updates all registered simple animations.\n'''
    for an in SimpleAnimation.simpleAnimations:
        an.update(dt)

        if an.ended: SimpleAnimation.simpleAnimations.remove(an)