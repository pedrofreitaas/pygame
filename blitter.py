import pygame as pg
from random import randint
from time import time as tm

def rotCenter(image, angle):
    """Rotate an image while keeping its center and size and returns the rotated image."""

    origRect = image.get_rect()
    rotatedImage = pg.transform.rotate(image, angle)

    # centering the rotated rect.
    rotatedRect = origRect.copy()
    rotatedRect.center = rotatedImage.get_rect().center

    # cutting the rotated image.
    rotatedImage = rotatedImage.subsurface(rotatedRect).copy()

    return rotatedImage

class Camera():
    def __init__(self, display_size) -> None:
        #REAL offset
        self.offset = pg.math.Vector2()
        self.delta_pos = pg.math.Vector2()

        #binarys
        self.locked = False
        self.shaking = False
        self.zooming = False

        #map infos
        self.map_size = [0,0]

        #display_infos
        self.display_size = display_size
    
    def setMapSize(self, map_size : list) -> None:
        self.map_size = map_size

    def lock(self) -> None:
        if not self.shaking:
            self.locked = True
    
    def unlock(self) -> None:
        if not self.shaking:
            self.locked = False

    def shake(self) -> None:
        if not self.shaking:
            self.shaking = True
            self.offset_befor_shaking = self.offset.copy()
        else:
            self.shaking = False
            self.offset = self.offset_befor_shaking.copy()
    
    def zoom(self) -> None:
        self.zooming = not self.zooming

    def yGoingOutLimit(self, camera_delta_) -> bool:
        future_y = self.offset[1] - camera_delta_[1]
        if future_y > 0 or abs(future_y) + self.display_size[1] >= self.map_size[1]:
            return True

        return False

    def xGoingOutLimit(self, camera_delta_) -> bool:
        future_x = self.offset[0] - camera_delta_[0]
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
        
    def update(self, camera_delta : pg.math.Vector2) -> None:
        """Moves the camera, based on the speed/delta given."""
        self.move(camera_delta)

class Layer():
    def __init__(self, display) -> None:
        #list with {images <-> cordinates}
        self.images = []

        self.display = display
        self.camera_sensible = True

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.images)

    def blitImages(self, Camera : Camera) -> None:
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

    def addImage(self, image : pg.surface, image_cord  : list) -> None:
        """Appends the image with the cords info given, in this layer."""
        self.images.append([image,image_cord])

    def reset(self) -> None:
        """Resets the instance."""
        self.images.clear()
    
class Blitter():
    def __init__(self, display, total_layers) -> None:
        self.display = display
        self.camera = Camera(self.display.get_size())

        #higher layers are blitted on top of the lowers
        self.layers = []

        #putting layers
        for i in range(total_layers):
            self.createLayer()

    def setCameraMapSize(self, map_size) -> None:
        """ Sets the map size inside the blitter camera instance."""
        self.camera.setMapSize(map_size)

    def cameraInfos(self) -> list:
        """ Returns: [cameraOFFSET, cameraDELTAPOS]."""
        return [self.camera.offset, self.camera.delta_pos]

    def lastLayer(self) -> Layer:
        """ Returns the last layer of the blitter instance."""
        return len(self.layers) - 1

    def UNlockCamera(self) -> None:
        """If the instance is unlocked, locks it, and does the oposite otherwise"""
        self.camera.locked = not self.camera.locked

    def changeCameraSensibility(self, layerIndex) -> None:
        """Changes the 'sensible' atribute of the given layer index."""
        self.layers[layerIndex].changeCameraSensibility()

    def createLayer(self) -> None:
        """Creates a new layer in the last position."""
        self.layers.append(Layer(self.display))

    def addImageInLayer(self, layerIndex : int, image : pg.surface, image_cord : list) -> None:
        """ adds the image in the chosen layer, with the coordinates of the parameter. """
        self.layers[layerIndex].addImage(image,image_cord)

    def displaySize(self) -> pg.math.Vector2:
        """Returns the size of the display of this instance."""
        return pg.math.Vector2(self.display.get_size())

    def reset(self) -> None:
        """Clears all images in the layer."""
        for layer in self.layers:
            layer.reset()

    def totalLayers(self) -> None:
        """Returns the amount of existing layers."""
        return len(self.layers)

    def cameraOffset(self) -> list:
        """Returns the OFFSET of the camera of this instance."""
        return self.camera.offset.copy()

    def totalImages(self) -> int:
        """Returns the amount of images stored in all the layers of this instance."""
        image_total = 0

        for layer in self.layers:
            image_total += layer.imageTotal()

        return image_total

    def update(self, camera_speed: pg.math.Vector2) -> None:
        """Updates the instance every call."""

        pg.display.flip()
        self.display.fill( (120,120,120) )
        
        self.camera.update(camera_speed)

        for layer in self.layers:
            layer.blitImages(self.camera)
            layer.reset()

