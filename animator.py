import pygame as pg
from math import floor

class Animator():
    '''EAP -> End Animation Procedure. It's a procedure that will be called at the end of the current animation.'''

    def __init__(self, sprites: pg.surface.Surface, imageSize: tuple[float,float], imagesPerLine: list[int]) -> None:
        """Initializes the animator.\n
           ImagesPerLine is a list that element correspond to the amount of sprites per line of the sprites(spritesheet).\n
           Basicaly, every element of the imagesPerLine represents how many images there is the line.\n
            example: 
           if imagesPerLine = [2,3,0,7], the instance will catch 2 imageSize subsurfaces of the first line of sprites image,\n
           three of the second, zero of the third, and seven of the last line line, that is the forth.\n"""
        
        self.going_foward: bool = True

        total_images = 0
        for i in imagesPerLine:
            total_images += i
        
        self.range_image: tuple[int, int] = [0, total_images - 1]

        self.sprites: list[pg.surface.Surface] = []
        
        self.loadSprites(sprites, imageSize, imagesPerLine)
        
        self.index_image: int = 0
        self.image: pg.surface.Surface = self.sprites[self.index_image]

        #booleans
        self.flipH: bool = False
        self.flipV: bool = False

        self.stopAt: bool = False
        self.stop_percentage: float = 1

        self.upd_coeficient: float = 6

        self.EAP: callable = lambda: None 

    def setEAP(self, proc: callable) -> None:
        '''Sets the animator to call the proc parameter in the end of the animation.\n'''
        self.EAP = proc

    def currentSpriteSize(self) -> tuple:
        # returns the rect size of the current sprite in the animation.
        return self.image.get_size()

    def animationPercentage(self) -> float:
        '''Returns a float number from zero to one, that represents the total sprites that have passed in the current animation.\n'''
        total_sprites = self.range_image[1] - self.range_image[0]
        return (self.index_image - self.range_image[0]) / total_sprites
        
    def loadSprites(self, spritesheet: pg.surface.Surface, imageSize: tuple[float,float], imagesPerLine: list[int]) -> None:
        """Adds the full spritesheet at once. Can be called to add sprites.\n"""

        for yIndex in range( len(imagesPerLine) ):
            for xIndex in range( imagesPerLine[yIndex] ):
                self.sprites.append( spritesheet.subsurface( (xIndex*imageSize[0], yIndex*imageSize[1]), imageSize).convert_alpha() )

    def getTotalImages(self):
        return len(self.sprites)

    def checkCallEAP(self) -> None:
        '''Checks if the end of animation procedure needs to be called.\n'''
        if self.index_image >= self.range_image[1]: self.EAP()
        if self.index_image < self.range_image[0]: self.EAP()

    def updateImage(self, dt: float) -> None:
        '''Updates the image variable of the instance to hold the next sprite of the animation, based on it's configs.\n
           The animation can go foward/backward and be cyclic/stopAt.\n'''

        # updating the index image.
        if self.going_foward: self.index_image += self.upd_coeficient * dt
        else: self.index_image -= self.upd_coeficient * dt

        self.checkCallEAP()
        
        # moving the animation cycle according to the configs. (foward/backward and cyclic/stopAt)
        if self.index_image > self.range_image[1] and not self.stopAt: self.index_image = self.range_image[0]
        
        elif self.index_image < self.range_image[0] and not self.stopAt: self.index_image = self.range_image[1]
        
        elif self.index_image > self.range_image[1] and self.stopAt: self.index_image = int(self.range_image[0]+ ((self.range_image[1]-self.range_image[0])*self.stop_percentage) )
        
        elif self.index_image < self.range_image[0] and self.stopAt: self.index_image = int(self.range_image[0]+ ((self.range_image[1]-self.range_image[0])*self.stop_percentage))
        
        self.image = pg.transform.flip(self.sprites[floor(self.index_image)], self.flipH, self.flipV)

    def flipHorizontally(self) -> None:
        """Sets the flipH boolean.\n"""
        self.flipH = True
    
    def flipVertically(self) -> None:
        """Sets the flipV boolean.\n"""
        self.flipV = True

    def activateStopAt(self, percentage: float) -> None:
        """Activates stopAt condition.\n
           OBS: stopAt if activated will stop the animation when the animation reaches the percentage in the parameter.\n
           Throws ValueError if the percentage is smaller than 0 or bigger than one.\n"""
        if percentage < 0 or percentage > 1:
            raise ValueError
        
        self.stopAt = True
        if self.going_foward: self.stop_percentage = percentage
        else: self.stop_percentage = 1 - percentage

    def deactivateStopAt(self) -> None:
        """Deactivates stopAt condition.\n"""
        self.stopAt = False

    def setRange(self, range: tuple[int,int]) -> None:
        """Sets the range of the change in image. Automatically deactivates the stopAt condition.\n
           OBS: 
           ->if the stopAt condition is True, when the animation gets to where it was set, it will\n
           repeat the last sprites until the codition is deactivated.\n
           ->Automatically sets the animation to the beggining of the new range.\n
           ->Does nothing if the current range is equal to the paramater.\n
           """

        if self.range_image == range: return
        
        self.range_image = range
        self.deactivateStopAt()

        if self.going_foward: self.index_image = self.range_image[0]
        else: self.index_image = self.range_image[1]

    def resetAnimation(self) -> None:
        """Reset the animation back to the first sprite of the animation.\n"""
        if self.going_foward: self.index_image = self.range_image[0]
        else: self.index_image = self.range_image[1]

    def goFurther(self) -> None:
        """Advances the animation in one sprite.\n"""

        if self.going_foward: self.index_image = int(self.index_image) + 1
        else: self.index_image = int(self.index_image) - 1

        if self.index_image >= self.range_image[1]:
            self.index_image = 0

        if self.index_image <= self.range_image[0]:
            self.index_image = self.range_image[1]

    def goBackwards(self) -> None:
        """Makes the animation go back one sprite.\n"""

        if self.going_foward: self.index_image = int(self.index_image) - 1
        else: self.index_image = int(self.index_image) + 1

        if self.index_image >= self.range_image[1]:
            self.index_image = 0

        if self.index_image <= self.range_image[0]:
            self.index_image = self.range_image[1]

    def invertMotion(self) -> None:
        """If the animation is going foward, makes it go backwards.\n
           If it's moving backwards, makes it move foward.\n"""
        self.going_foward = not self.going_foward

    def resizeSprites(self, size: tuple[float,float]) -> None:
        """Resizes all the sprites with the given size.\n"""
        for ind, sprite in enumerate(self.sprites):
            self.sprites[ind] = pg.transform.smoothscale(sprite, size)

    def changeUpdateCoeficient(self, coeficient: float) -> None:
        '''Changes the upd coeficient based on the parameter.\n
           The higher the update coeficient, the faster the animation will pass.\n'''
        
        self.upd_coeficient = coeficient

    def update(self, dt: float) -> None:
        """Moves the animation according to the motion of the animator.\n
           The coeficient is updated to it's original value.\n
           The flips booleans are updated to false.
           Sets the end animation procedure to function that does nothing.\n"""
        
        self.updateImage(dt)

        #reseting variables.
        self.EAP = lambda: None
        self.flipH = False
        self.flipV = False
        self.upd_coeficient = 6
  