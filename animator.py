import pygame as pg
from math import floor

class Animator():
    def __init__(self, sprites: pg.image, imageSize: list, imagesPerLine: list) -> None:
        """Initializes the animator.
            ImagesPerLine is a list that element correspond to the amount of sprites per line of the sprites(spritesheet).
            Basicaly, every element of the imagesPerLine represents how many images there is the line.
            ex: 
            if imagesPerLine = [2,3,0,7], the instance will catch 2 imageSize subsurfaces of the first line of sprites image,
            three of the second, zero of the third, and seven of the last line line, that is the forth."""
        
        self.going_foward = True

        total_images = 0
        for i in imagesPerLine:
            total_images += i
        
        self.range_image = [0, total_images - 1]

        self.sprites = []
        
        self.loadSprites(sprites, imageSize, imagesPerLine)
        
        self.index_image = 0
        self.image = self.sprites[self.index_image]

        #booleans
        self.flipH = False
        self.flipV = False
        self.stopAtEnd = False

        self.upd_coeficient = 6

    def scaleImage(self, factor: int) -> None:
        """"Scales the original instance's image by the given factor."""
        self.scale_factor = factor

    def currentSpriteSize(self) -> tuple:
        # returns the rect size of the current sprite in the animation.
        return self.image.get_size()

    def loadSprites(self, spritesheet : pg.image, imageSize: list, imagesPerLine: list) -> None:
        """Adds the full spritesheet at once. Can be called to add sprites."""

        for yIndex in range( len(imagesPerLine) ):
            for xIndex in range( imagesPerLine[yIndex] ):
                self.sprites.append( spritesheet.subsurface( (xIndex*imageSize[0], yIndex*imageSize[1]), imageSize).convert_alpha() )

    def getTotalImages(self):
        return len(self.sprites)

    def updateImage(self, dt: float) -> None:
        if self.going_foward:
            self.index_image += self.upd_coeficient * dt
        else:
            self.index_image -= self.upd_coeficient * dt

        if self.index_image >= self.range_image[1] and not self.stopAtEnd:
            self.index_image = self.range_image[0]

        elif self.index_image < self.range_image[0] and not self.stopAtEnd:
            self.index_image = self.range_image[1]

        # the animation will consist in the last two sprites
        elif self.index_image >= self.range_image[1] and self.stopAtEnd:
            self.index_image = self.range_image[1] -2
        
        # the animation will consist in the first two sprites.
        elif self.index_image < self.range_image[0] and self.stopAtEnd:
            self.index_image = self.range_image[0] +2
        
        self.image = pg.transform.flip(self.sprites[floor(self.index_image)], self.flipH, self.flipV)

    def flipHorizontally(self) -> None:
        """Sets the flipH boolean."""
        self.flipH = True
    
    def flipVertically(self) -> None:
        """Sets the flipV boolean."""
        self.flipV = True

    def activateStopAtEnd(self) -> None:
        """Activates stopAtEnd condition.
           OBS: stopAtEnd condition: stops the animation when it reaches the last sprites if activated."""
        
        self.stopAtEnd = True

    def deactivateStopAtEnd(self) -> None:
        """Deactivates stopAtEnd condition."""
        self.stopAtEnd = False

    def setRange(self, range: list) -> None:
        """Sets the range of the change in image. Automatically deactivates the stopAtEnd condition.
           OBS: if the stopAtEnd condition is True, when the animation gets to the last sprite, it will
           repeat the two last sprites until the codition is deactivated."""
        
        self.range_image = range
        self.deactivateStopAtEnd()

    def resetAnimation(self) -> None:
        """Reset the animation back to the first sprite of the animation."""
        self.index_image = self.range_image[0]

    def goFurther(self) -> None:
        """Advances the animation one sprite foward at once."""

        self.index_image = int(self.index_image) + 1
        if self.index_image >= self.range_image[1]:
            self.index_image = 0

    def goBackwards(self) -> None:
        """Makes the animation go back one sprite at once."""

        self.index_image = int(self.index_image) - 1
        if self.index_image <= self.range_image[0]:
            self.index_image = self.range_image[1]

    def invertMotion(self) -> None:
        """If the animation is going foward, makes it go backwards, if it's moving backwards, makes it move foward."""
        self.going_foward = not self.going_foward

    def resizeSprites(self, size: tuple) -> None:
        """Resizes all the sprites with the given size."""
        for ind, sprite in enumerate(self.sprites):
            self.sprites[ind] = pg.transform.smoothscale( sprite, size )

    def update(self, dt: float) -> None:
        """Moves the animation according to the motion of the animator, the coeficient given."""
        
        self.updateImage(dt)
        self.flipH = self.flipV = False
        self.upd_coeficient = 6
  