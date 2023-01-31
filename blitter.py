import pygame as pg
from random import randint
from time import time as tm

def rotCenter(image: pg.surface.Surface, angle: float):
    """Rotate an image while keeping its center and size and returns the rotated image.\n"""

    origRect = image.get_rect()
    rotatedImage = pg.transform.rotate(image, angle)

    # centering the rotated rect.
    rotatedRect = origRect.copy()
    rotatedRect.center = rotatedImage.get_rect().center

    # cutting the rotated image.
    rotatedImage = rotatedImage.subsurface(rotatedRect).copy()

    return rotatedImage

class Camera():
    def __init__(self, display_size: tuple[float,float]) -> None:
        #REAL offset
        self.offset: pg.math.Vector2 = pg.math.Vector2()
        self.delta_pos: pg.math.Vector2 = pg.math.Vector2()

        #binarys
        self.locked: bool = False
        self.shaking: bool = False
        self.zooming: bool = False

        #map infos
        self.map_size: tuple[float,float] = [0,0]

        #display_infos
        self.display_size: tuple[float,float]= display_size
    
    def setMapSize(self, map_size : tuple[float,float]) -> None:
        '''Sets the instance's map size with the given parameter.\n'''
        self.map_size = map_size

    def lock(self) -> None:
        '''Looks camera offset.\n'''
        if not self.shaking:
            self.locked = True
    
    def unlock(self) -> None:
        '''Unlocks camera offset.\n'''
        if not self.shaking:
            self.locked = False

    def shake(self) -> None:
        '''Triggers a continuous change in the offeset to simulate a shake.\n'''
        if not self.shaking:
            self.shaking = True
            self.offset_befor_shaking = self.offset.copy()
        else:
            self.shaking = False
            self.offset = self.offset_befor_shaking.copy()
    
    def zoom(self) -> None:
        '''Trigers zoom.\n'''
        self.zooming = not self.zooming

    def yGoingOutLimit(self, camera_delta: pg.math.Vector2) -> bool:
        '''Check if the camera y is going out the map limits.\n'''
        future_y = self.offset[1] - camera_delta[1]
        if future_y > 0 or abs(future_y) + self.display_size[1] >= self.map_size[1]:
            return True

        return False

    def xGoingOutLimit(self, camera_delta: pg.math.Vector2) -> bool:
        '''Check if the camera x is going out the map limits.\n'''
        future_x = self.offset[0] - camera_delta[0]
        if future_x > 0 or abs(future_x) + self.display_size[0] >= self.map_size[0]:
            return True
        return False

    def move(self, camera_delta : pg.math.Vector2) -> None:
        """Moves the instance if not locked.
           Shakes if it is shaking."""

        if self.locked:
            self.delta_pos = pg.math.Vector2()
            return

        if self.shaking:
            random_shake = pg.math.Vector2(randint(-5,5), randint(-5,5))
            self.offset = self.offset + random_shake
            self.delta_pos = self.delta_pos + random_shake
        
        #Setting real offset
        self.delta_pos = pg.math.Vector2()

        if not self.xGoingOutLimit(camera_delta):
            self.offset[0] = self.offset[0] - camera_delta[0]
            self.delta_pos[0] = camera_delta[0]
        if not self.yGoingOutLimit(camera_delta):
            self.offset[1] = self.offset[1] - camera_delta[1]
            self.delta_pos[1] = camera_delta[1]
        
    def update(self, camera_delta: pg.math.Vector2) -> None:
        """Moves the camera, based on the speed/delta given."""
        self.move(camera_delta)

class Layer():
    def __init__(self, display: pg.surface.Surface) -> None:
        #list with {images <-> cordinates}
        self.images: list[pg.surface.Surface] = []

        self.display: pg.surface.Surface = display
        self.camera_sensible: bool = True

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.images)

    def blitImages(self, Camera: Camera) -> None:
        """Blits all the images of the instance. 
           If the layer is sensible to OFFSET, subtracts the cords stored by the OFFSET.
           IF "" isn't "", blits the image in the given cords.
           OBS: Prints with zoom, or shakes it according to the booleans of the instance"""

        if not self.camera_sensible:
            for image in self.images:
                if Camera.zooming:
                    self.display.blit(pg.transform.scale2x(image[0]), image[1])
                else:
                    self.display.blit(image[0], image[1])
            return

        for image in self.images:
            pos = image[1] + Camera.offset

            if Camera.zooming:
                self.display.blit(pg.transform.scale2x(image[0]), pos)
            else:
                self.display.blit(image[0], pos)

    def addImage(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer."""
        self.images.append([image,image_cord])

    def reset(self) -> None:
        """Resets the instance."""
        self.images.clear()
    
class Blitter():
    def __init__(self, display: pg.surface.Surface, total_layers: int) -> None:
        self.display: pg.surface.Surface = display
        self.camera: Camera = Camera(self.display.get_size())

        #higher layers are blitted on top of the lowers
        self.layers: list[Layer] = []

        #putting layers
        for i in range(total_layers):
            self.createLayer()

    def setCameraMapSize(self, map_size: tuple[float,float]) -> None:
        """ Sets the map size inside the blitter camera instance.\n"""
        self.camera.setMapSize(map_size)

    def lastLayer(self) -> Layer:
        """ Returns the last layer of the blitter instance.\n"""
        return len(self.layers) - 1

    def UNlockCamera(self) -> None:
        """If the instance is unlocked, locks it, and does the oposite otherwise.\n"""
        self.camera.locked = not self.camera.locked

    def changeCameraSensibility(self, layerIndex: int) -> None:
        """Changes the 'sensible' atribute of the given layer index.\n"""
        self.layers[layerIndex].changeCameraSensibility()

    def createLayer(self) -> None:
        """Creates a new layer in the last position.\n"""
        self.layers.append(Layer(self.display))

    def addImageInLayer(self, layerIndex: int, image: pg.surface.Surface, image_cord: pg.math.Vector2) -> None:
        """ adds the image in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addImage(image,image_cord)

    def displaySize(self) -> pg.math.Vector2:
        """Returns the size of the display of this instance.\n"""
        return pg.math.Vector2(self.display.get_size())

    def reset(self) -> None:
        """Clears all images in the layer.\n"""
        for layer in self.layers:
            layer.reset()

    def totalLayers(self) -> None:
        """Returns the amount of existing layers.\n"""
        return len(self.layers)

    def cameraOffset(self) -> pg.math.Vector2:
        """Returns the OFFSET of the camera of this instance.\n"""
        return self.camera.offset

    def totalImages(self) -> int:
        """Returns the amount of images stored in all the layers of this instance.\n"""
        image_total = 0

        for layer in self.layers:
            image_total += layer.imageTotal()

        return image_total

    def update(self, camera_speed: pg.math.Vector2) -> None:
        """Updates the instance every call.\n"""

        pg.display.flip()
        self.display.fill( (120,120,120) )
        
        self.camera.update(camera_speed)

        for layer in self.layers:
            layer.blitImages(self.camera)
            layer.reset()
