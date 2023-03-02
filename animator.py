import pygame as pg

class Animator():
    '''EAP -> End Animation Procedure. It's a procedure that will be called at the end of the current animation.'''

    def __init__(self, sprites: pg.surface.Surface, imageSize: tuple[float,float], imagesPerLine: list[int]) -> None:
        """Initializes the animator.\n
           ImagesPerLine is a list that element correspond to the amount of sprites per line of the sprites(spritesheet).\n
           Basicaly, every element of the imagesPerLine represents how many images there is the line.\n
            example: 
           if imagesPerLine = [2,3,0,7], the instance will catch 2 imageSize subsurfaces of the first line of sprites image,\n
           three of the second, zero of the third, and seven of the last line line, that is the forth.\n"""
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
        self.new_range: bool = True

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
        total_sprites = self.range_image[1] - self.range_image[0] + 1
        return (self.index_image - self.range_image[0]) / total_sprites
        
    def loadSprites(self, spritesheet: pg.surface.Surface, imageSize: tuple[float,float], imagesPerLine: list[int]) -> None:
        """Adds the full spritesheet at once. Can be called to add sprites.\n"""

        for yIndex in range( len(imagesPerLine) ):
            for xIndex in range( imagesPerLine[yIndex] ):
                self.sprites.append( spritesheet.subsurface( (xIndex*imageSize[0], yIndex*imageSize[1]), imageSize).convert_alpha() )

    def getTotalImages(self):
        return len(self.sprites)

    def checkCallEAP(self) -> None:
        '''Checks if the end of animation procedure needs to be called.\n
           Doesn't call EAP with if a new range was setted and yet not took effect.\n'''
        if self.new_range: 
            self.new_range = False
            return
        
        if self.index_image >= self.range_image[1]: self.EAP()

    def updateImage(self, dt: float) -> None:
        '''Updates the image variable of the instance to hold the next sprite of the animation, based on it's configs.\n
           The animation can go foward/backward and be cyclic/stopAt.\n'''

        self.index_image += self.upd_coeficient * dt
        self.checkCallEAP()
    
        if self.index_image > self.range_image[1]: self.index_image = self.range_image[0]
        elif self.index_image < self.range_image[0]: self.index_image = self.range_image[0] # just for safety
        
        self.image = pg.transform.flip(self.sprites[int(self.index_image)], self.flipH, self.flipV)

    def flipHorizontally(self) -> None:
        """Sets the flipH boolean.\n"""
        self.flipH = True
    
    def flipVertically(self) -> None:
        """Sets the flipV boolean.\n"""
        self.flipV = True

    def resizeRange(self, begin_sprite: int, end_sprite: int) -> None:
        """Sets the animation to be a 'sub animation' of itself.\n
           Only operates if the current animation has reached the begin_sprite parameter stage.\n
           The number parameters should be the indexes of the sprites considering the current animation.\n
           Ex: self.resizeRange(3,7) would consider the third/seventh sprites of the current animation.\n"""
        if int(self.index_image - self.range_image[0]) < begin_sprite: return

        animation_total_spr = self.range_image[1]-self.range_image[0]

        if begin_sprite < 1 or end_sprite > animation_total_spr: raise ValueError

        new_range: tuple[int,int] = (self.range_image[0] + begin_sprite-1,
                                     self.range_image[0] + end_sprite )

        self.setRange( new_range )

    def setRange(self, range: tuple[int,int]) -> None:
        """Sets the range of the change in image.\n"""
        if range[1] < range[0]: raise ValueError
        if range[1] < 0 or range[0] < 0: raise ValueError
        if range[1] >= self.getTotalImages(): raise ValueError

        if range != self.range_image: self.new_range = True

        self.range_image = range

    def resetAnimation(self) -> None:
        """Reset the animation back to the first sprite of the animation.\n"""
        self.index_image = self.range_image[0]

    def goFurther(self) -> None:
        """Advances the animation in one sprite.\n"""

        self.index_image = int(self.index_image) + 1

        if self.index_image >= self.range_image[1]:
            self.index_image = 0

    def goBackwards(self) -> None:
        """Makes the animation go back one sprite.\n"""

        self.index_image = int(self.index_image) - 1

        if self.index_image < self.range_image[0]: self.index_image = self.range_image[0]

    def resizeSprites(self, size: tuple[float,float]) -> None:
        """Resizes all the sprites with the given size.\n"""
        for ind, sprite in enumerate(self.sprites):
            self.sprites[ind] = pg.transform.scale(sprite, size)
        self.image = pg.transform.scale(self.image, size)

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
