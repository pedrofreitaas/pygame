from math import acos,degrees
import pygame as pg

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