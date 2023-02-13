import pygame as pg
from timer import *
from typing import Dict
from math import ceil, floor

class TileDict():
    '''Clears tiles every 10 seconds.\n'''
    
    def __init__(self, tiles_size: tuple[float,float]) -> None:
        self.tiles: Dict[str,int|None] = {}
        self.tiles_size: tuple[int,int] = tiles_size

        Timer(10, lambda: self.tiles.clear(), -1)

    def grid(self, pos: pg.math.Vector2|tuple[float,float]) -> tuple[int,int]:
        return [floor(pos[0]/self.tiles_size[0]), floor(pos[1]/self.tiles_size[1])]

    def key(self, grid: tuple[int,int]) -> str:
        return str(grid[0])+','+str(grid[1])

    def getID(self, pos: pg.math.Vector2) -> int|None:
        '''Returns the id stored in that pos.\n'''
        try:
            return self.tiles[ self.key( self.grid(pos) ) ]
        except KeyError:
            return None

    def setID(self, pos: pg.math.Vector2, ID: int|None) -> None:
        '''Sets the ID of the position to be the parameter.\n'''
        self.tiles[self.key(self.grid(pos))] = ID

    def update(self, rect: pg.rect.Rect, ID: int|None) -> None:
        '''Updates the content of the rect to the parameter ID.\n'''
        startGrid = self.grid( rect.topleft )

        grids_x = ceil( (rect.width+ rect.left%32)/self.tiles_size[0])
        grids_y = ceil( (rect.height+ rect.top%32)/self.tiles_size[1])

        for x in range(grids_x):
            for y in range(grids_y):
                self.tiles[ self.key( [x+startGrid[0],y+startGrid[1]] ) ] = ID

class Camera():
    def __init__(self) -> None:
        self.dt: float = 0
        self.previous_player_center: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.pos: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.speed_value: float = 20

        self.display_size: pg.math.Vector2 = pg.math.Vector2(pg.display.get_window_size())

        self.center_rect: pg.rect.Rect = self.captureRect().inflate(-400,-400)

        #map infos
        self.map_size: tuple[float,float] = self.display_size
    
    def setMapSize(self, map_size : tuple[float,float]) -> None:
        '''Sets the instance's map size with the given parameter.\n'''
        self.map_size = map_size
    
    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Gets the camera move speed.\n'''

        if not self.center_rect.collidepoint(self.previous_player_center+self.pos):
            fitVector = self.previous_player_center-pg.math.Vector2(self.center_rect.center)+self.pos
            self.pos -= fitVector.normalize()*self.dt*self.speed_value*10

        speed = self.speed_dir*self.dt*self.speed_value

        outXRigth = self.map_size[0] + self.pos[0]-self.display_size[0]
        outYBottom = self.map_size[1] + self.pos[1]-self.display_size[1]
        
        if self.pos[0] > 0: speed[0]=-self.pos[0]
        elif outXRigth < 0: speed[0]=-outXRigth
        
        if self.pos[1] > 0: speed[1]=-self.pos[1]
        elif outYBottom < 0: speed[1]=-outYBottom

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
        self.non_structs: list[tuple[pg.surface.Surface, pg.math.Vector2]] = []
        self.structs: list[tuple[pg.surface.Surface, pg.math.Vector2]] = []
        
        self.is_camera_sensible: bool = True

        self.display: pg.surface.Surface = display

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.non_structs)+len(self.structs)

    def addImage(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer"""
        self.non_structs.append([image,image_cord])

    def addStruct(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer"""
        self.structs.append([image,image_cord])

    def lightBlit(self) -> None:
        '''Blits the images without offset nor checking ids.\n'''
        for image in self.structs:
            self.display.blit(image[0], image[1])

        for image in self.non_structs:
            self.display.blit(image[0], image[1])

    def blit(self, offset: pg.math.Vector2, IDS: TileDict) -> None:
        '''Blits the images in the instance.\n'''
        if not self.is_camera_sensible: offset = pg.math.Vector2(0,0)

        for image in self.structs:
            self.display.blit(image[0], image[1]+offset)

        for image in self.non_structs:
            pos = image[1]+offset
            self.display.blit(image[0], pos)

            IDS.update( pg.rect.Rect(image[1], image[0].get_size()), None )

    def reset(self) -> None:
        """Resets the instance."""
        self.non_structs.clear()
        self.structs.clear()
    
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
        """Adds the image in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addImage(image,image_cord)

    def addStructInLayer(self, layerIndex: int, image: pg.surface.Surface, image_cord: pg.math.Vector2) -> None:
        """Adds the struct in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addStruct(image,image_cord)

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
    
    def lightBlit(self) -> None:
        '''Blits all the images in the layers, taking less perfomance.\n'''
        for layer in self.layers:
            layer.lightBlit()

    def blit(self, IDS: TileDict) -> None:
        '''Blits all the images in the layers.\n'''
        for layer in self.layers:
            layer.blit(self.camera.pos, IDS)
    
    def lightUpdate(self) -> None:
        '''Updates instance withou handling: Struct IDs, Camera.\n'''
        self.lightBlit()
        self.reset()

        pg.display.flip()

    def update(self, dt: float, player_center: pg.math.Vector2, IDS: TileDict) -> None:        
        '''Updates the instance handling: Camera, Struct IDs.\n'''
        self.blit(IDS)
        self.reset()

        self.camera.update(dt, player_center)
        pg.display.flip()

        updateTimers()