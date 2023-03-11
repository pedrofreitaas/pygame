from math import acos,degrees
import pygame as pg

class KeyboardIcons():
    
    def __init__(self) -> None:

        allIcons = pg.image.load('assets/game/keyicons.png').convert_alpha()

        self.keySize = (16,16)

        self.UNpressed_keys_icons: list[pg.surface.Surface] = []
        UNpressed = allIcons.subsurface((0,0), (128,7*16))
        self.loadUNpressedKeys(UNpressed)

        self.pressed_keys_icons: list[pg.surface.Surface] = []
        pressed = allIcons.subsurface((0,7*16), (128,7*16))
        self.loadPressedKeys(pressed)

    def loadUNpressedKeys(self, allIcons: pg.surface.Surface) -> None:
        '''Loads keyboard unpressed keys into instace.\n'''
        keysPerLine = (8,8,8,8,8,8,6)

        self.UNpressed_keys_icons = []
        for yIndex in range( len(keysPerLine) ):
            for xIndex in range( keysPerLine[yIndex] ):
                self.UNpressed_keys_icons.append( allIcons.subsurface( (xIndex*self.keySize[0], yIndex*self.keySize[1]), self.keySize).convert_alpha() )

    def loadPressedKeys(self, allIcons: pg.surface.Surface) -> None:
        '''Loads keyboard pressed keys into instance.\n'''
        keysPerLine = (8,8,8,8,8,8,6)

        self.pressed_keys_icons = []
        for yIndex in range( len(keysPerLine) ):
            for xIndex in range( keysPerLine[yIndex] ):
                self.pressed_keys_icons.append( allIcons.subsurface( (xIndex*self.keySize[0], yIndex*self.keySize[1]), self.keySize).convert_alpha() )

    def getIcon(self, index: int, pressed: bool) -> pg.surface.Surface:
        if pressed: return self.pressed_keys_icons[index] 
        else: return self.UNpressed_keys_icons[index]
    
    def getLetter(self, letter: str, pressed: bool) -> pg.surface.Surface:
        if len(letter) > 1: raise ValueError
        letter = letter.capitalize()
        return self.getIcon(16+ord(letter)-ord('A'), pressed)

keyboardIcons = KeyboardIcons()

def inInterval(interval: tuple[float|None,float|None], numb: float) -> bool:
    '''Return true if the numb paramater is inside the interval parameter, like this: [a,b).
       Set the interval's end/begin with None to ignore that limit.\n'''
    if interval[0] != None and numb < interval[0]: return False
    if interval[1] != None and numb >= interval[1]: return False
    return True

def angle(vec1: pg.math.Vector2, vec2: pg.math.Vector2, smaller: bool=True) -> float:
    '''Returns the smallest angle between two vectors if smaller flag = True.\n'''
    vec1_norm = vec1.length()
    vec2_norm = vec2.length()

    cos = vec1 * vec2 / (vec1_norm * vec2_norm)
                        
    if smaller: return degrees(acos(cos))
    return 360-degrees(acos(cos))

def rotCenter(image: pg.surface.Surface, angle: float) -> None:
    """Rotate an image while keeping its center and size and returns the rotated image.\n"""
    origRect = image.get_rect()
    rotatedImage = pg.transform.rotate(image, angle)

    # centering the rotated rect.
    rotatedRect = origRect.copy()
    rotatedRect.center = rotatedImage.get_rect().center

    # cutting the rotated image.
    rotatedImage = rotatedImage.subsurface(rotatedRect).copy()

    return rotatedImage
