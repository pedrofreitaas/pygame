import pygame as pg
from random import randint

class Camera():
    def __init__(self) -> None:
        self.dt: float = 0
        self.previous_player_center: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.pos: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.speed_value: float = 80

        self.display_size: pg.math.Vector2 = pg.math.Vector2(pg.display.get_window_size())

        self.center_rect: pg.rect.Rect = self.captureRect().inflate(-400,-400)

        #map infos
        self.map_size: tuple[float,float] = self.display_size
    
    def setMapSize(self, map_size : tuple[float,float]) -> None:
        '''Sets the instance's map size with the given parameter.\n'''
        self.map_size = map_size
    
    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Gets the camera move speed.\n'''
        speed = self.speed_dir*self.dt*self.speed_value

        outXRigth = self.map_size[0] + self.pos[0]-self.display_size[0]
        outYBottom = self.map_size[1] + self.pos[1]-self.display_size[1]

        if self.pos[0] > 0: speed[0]=-self.pos[0]
        elif outXRigth < 0: speed[0]=-outXRigth
        
        if self.pos[1] > 0: speed[1]=-self.pos[1]
        elif outYBottom < 0: speed[1]=-outYBottom

        if not self.center_rect.collidepoint(self.previous_player_center+self.pos):
            fitVector = self.previous_player_center-pg.math.Vector2(self.center_rect.center)+self.pos
            self.pos -= fitVector.normalize()*self.dt*self.speed_value*3

        return speed

    def move(self) -> None:
        """Moves the instance.\n"""
        self.pos = self.pos + self.getMovementSpeed()
    
    def captureRect(self) -> pg.rect.Rect:
        '''Returns the rect that the camera is displaying.\n'''
        return pg.rect.Rect(-self.pos, self.display_size)

    def getPlayerDP(self, player_center: pg.math.Vector2) -> pg.math.Vector2:
        '''Returns player delta pos.\n'''
        dp = player_center - self.previous_player_center
        self.previous_player_center = player_center

        return dp

    def update(self, dt: float, player_center: pg.math.Vector2) -> None:
        """Moves the camera, based on the speed/delta given.\n"""

        playerDP = self.getPlayerDP(player_center) 
        
        if playerDP != pg.math.Vector2(0,0): self.speed_dir = playerDP.normalize()
        else: self.speed_dir = playerDP

        self.dt = dt
        self.move()

class Layer():
    def __init__(self, display: pg.surface.Surface) -> None:
        #list with {images <-> cordinates}
        self.images: list[pg.surface.Surface, pg.math.Vector2] = []
        self.is_camera_sensible: bool = True

        self.display: pg.surface.Surface = display

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.images)

    def addImage(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer."""
        self.images.append([image,image_cord])

    def reset(self) -> None:
        """Resets the instance."""
        self.images.clear()
    
class Blitter():
    def __init__(self, display: pg.surface.Surface, total_layers: int) -> None:
        self.display: pg.surface.Surface = display
        self.display_rect: pg.rect.Rect = display.get_rect()
        self.camera: Camera = Camera()

        #higher layers are blitted on top of the lowers
        self.layers: list[Layer] = []

        #putting layers
        for i in range(total_layers):
            self.createLayer()

    def setCameraMapSize(self, map_size: tuple[float,float]) -> None:
        """ Sets the map size inside the blitter camera instance.\n"""
        self.camera.setMapSize(map_size)
    
    def changeLayerCameraSensibility(self, layer_idx: int, sens: bool) -> None:
        '''Makes the layer sensible to camera, or not.\n'''
        self.layers[layer_idx].is_camera_sensible = sens

    def lastLayer(self) -> Layer:
        """ Returns the last layer of the blitter instance.\n"""
        return len(self.layers) - 1

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

    def totalImages(self) -> int:
        """Returns the amount of images stored in all the layers of this instance.\n"""
        image_total = 0

        for layer in self.layers:
            image_total += layer.imageTotal()

        return image_total

    def blit(self) -> None:
        '''Blits all the images in the layers.\n'''
        for layer in self.layers:
            offset = pg.math.Vector2()

            if layer.is_camera_sensible: offset = self.camera.pos

            for image in layer.images:
                self.display.blit(image[0], offset+image[1])
    
    def update(self, dt: float, player_center: pg.math.Vector2) -> None:
        self.display.fill( (120,120,120) )
        
        self.camera.update(dt, player_center)

        self.blit()

        self.reset()

        pg.display.flip()
