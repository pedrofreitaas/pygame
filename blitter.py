import pygame as pg
from json import load, dumps
from io import open

class Camera():
    def __init__(self, pos: pg.math.Vector2, map_size: tuple[float,float]=None) -> None:
        '''Sets map's size with display size, if map_size parameter is default.\n'''
        self.dt: float = 0

        self.pos: pg.math.Vector2 = pos
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.speed_value: float = 32

        self.display_rect: pg.rect.Rect = pg.rect.Rect(pg.display.get_surface().get_rect())
        self.center_rect: pg.rect.Rect = self.display_rect.inflate(-400,-400)

        #map infos
        if map_size == None: self.map_size: tuple[float,float] = pg.display.get_window_size()
        else: self.map_size: tuple[float, float] = map_size

        #booleans
        self.is_lock = False
    
    def UNlock(self) -> None:
        '''Locks or unlocks the camera.\n'''
        self.is_lock = not self.is_lock

    def setMapSize(self, map_size : tuple[float,float]) -> None:
        '''Sets the instance's map size with the given parameter.\n'''
        self.map_size = map_size

    def getPos(self) -> pg.math.Vector2:
        return self.pos.copy()

    def getOffsetted(self, vec: pg.math.Vector2) -> pg.math.Vector2:
        '''Returns the vector offsetted by instance.\n'''
        return vec+self.pos

# movement.
    def fitInsideMap(self) -> None:
        '''Automatically fits the instance inside the map's limits.\n'''
        outXRigth = self.map_size[0] + self.pos[0]-self.display_rect.width
        outYBottom = self.map_size[1] + self.pos[1]-self.display_rect.height
        
        if self.pos[0] > 0: self.pos[0]=0
        elif outXRigth < 0: self.pos[0]-=outXRigth
        
        if self.pos[1] > 0: self.pos[1]=0
        elif outYBottom < 0: self.pos[1]-=outYBottom

    def getMovementSpeed(self, player_center: pg.math.Vector2) -> pg.math.Vector2:
        '''Gets the camera move speed.\n'''
        speed = pg.math.Vector2(0,0)

        player_center_O = self.getOffsetted(player_center)

        if not self.center_rect.collidepoint(player_center_O):
            fitVector = player_center_O -pg.math.Vector2(self.center_rect.center)
            speed -= fitVector.normalize()*self.dt*self.speed_value*10

        return speed

    def move(self, player_center: pg.math.Vector2) -> None:
        """Moves the instance.\n"""
        self.pos = self.pos + self.getMovementSpeed(player_center)

        self.fitInsideMap()
# -------------- #

# camera Rects.
    def getCaptureRect(self) -> pg.rect.Rect:
        '''Returns the rect that represents the area of coordinates that is been displayed.\n'''
        return pg.rect.Rect( -self.pos, (self.display_rect.width, self.display_rect.height) )

    def getDisplayRect(self) -> pg.rect.Rect:
        return self.display_rect

    def fitsDisplayRect(self, rect: pg.rect.Rect) -> bool:
        '''Returns true if the rect dislocated by the offset is in the display.\n'''
        return self.display_rect.contains( rect.move(self.pos) )
# ------------------- #

    def update(self, dt: float, player_center: pg.math.Vector2) -> None:
        """Moves the camera, based on the speed/delta given.\n
           Does not update if locked.\n"""
        if self.is_lock: return

        self.dt = dt
        self.move(player_center)
    
    def __del__(self) -> None:
        '''Saves camera infos in json file.\n'''
        cameraInfos: dict = {}

        try:
            with open('infos/game.json', 'r') as file:
                cameraInfos = load(file)
        except:
            with open('infos/game.json', 'w') as file:
                file.write( dumps({}) )

        infos = {
            'x': self.pos[0],
            'y': self.pos[1],
            'map_size_x': self.map_size[0],
            'map_size_y': self.map_size[1]
        }

        cameraInfos['camera'] = infos

        with open('infos/game.json', 'w') as file:
            file.write( dumps(cameraInfos, indent=2) )

class Layer():
    def __init__(self, display: pg.surface.Surface) -> None:
        self.images: list[tuple[pg.surface.Surface, pg.math.Vector2]] = []
        self.is_camera_sensible: bool = True
        self.display: pg.surface.Surface = display

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.images)
    
    def reset(self) -> None:
        """Resets the instance."""
        self.images.clear()
    
# adding registers functions.
    def addImage(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer"""
        self.images.append((image,image_cord))
#-------------------------------- #

# blit functions.
    def blit(self, offset: pg.math.Vector2) -> None:
        if self.is_camera_sensible: self.blitOffsetWise(offset)
        else: self.blitNotOffsetWise()

    def blitOffsetWise(self, offset: pg.math.Vector2) -> None:
        '''Blits the layer's images counting the offset.\n'''        
        for image, pos in self.images:
            pos = pos + offset
            self.display.blit(image,pos)

    def blitNotOffsetWise(self) -> None:
        '''Blits the instance's images without couting for offsets.\n'''
        for image, pos in self.images:
            self.display.blit(image,pos)

def createCameraFromJson() -> Camera:
    '''Creates and returns a camera instance created from json data.\n
       Json syntax:\n
       {
        "camera": {
            "x": float,
            "y": float
            "map_pos_x": float,
            "map_pos_y": float,
            }
        }'''
    cameraInfos: dict = {}

    try:
        with open('infos/game.json', 'r') as file:
            gameInfos = load(file)

            cameraInfos = gameInfos['camera']

            offset = pg.math.Vector2(cameraInfos['x'], cameraInfos['y'])
            map_size = (cameraInfos['map_size_x'], cameraInfos['map_size_y'])

            return Camera(offset, map_size)
    
    except:
        return Camera( pg.math.Vector2(0,0) )

class Blitter():
    def __init__(self, display: pg.surface.Surface, total_layers: int) -> None:
        self.display: pg.surface.Surface = display
        self.display_rect: pg.rect.Rect = display.get_rect()

        self.camera: Camera = createCameraFromJson()

        #higher layers are blitted on top of the lowers
        self.layers: list[Layer] = []

        #putting layers
        for i in range(total_layers): self.createLayer()

# getting values.
    def lastLayer(self) -> Layer:
        """ Returns the last layer of the blitter instance.\n"""
        return len(self.layers) - 1

    def totalLayers(self) -> None:
        """Returns the amount of existing layers.\n"""
        return len(self.layers)

    def totalImages(self) -> int:
        """Returns the amount of images stored in all the layers of this instance.\n"""
        image_total = 0

        for layer in self.layers:
            image_total += layer.imageTotal()

        return image_total

    def displaySize(self) -> pg.math.Vector2:
        """Returns the size of the display of this instance.\n"""
        return pg.math.Vector2(self.display.get_size())
# --------------------- #

# setting values.
    def setCameraMapSize(self, map_size: tuple[float,float]) -> None:
        """ Sets the map size inside the blitter camera instance.\n"""
        self.camera.setMapSize(map_size)
    
    def changeLayerCameraSensibility(self, layer_idx: int, sens: bool) -> None:
        '''Makes the layer sensible to camera, or not.\n'''
        self.layers[layer_idx].is_camera_sensible = sens

    def createLayer(self) -> None:
        """Creates a new layer in the last position.\n"""
        self.layers.append(Layer(self.display))

    def addImage(self, layerIndex: int, image: pg.surface.Surface, image_cord: pg.math.Vector2) -> None:
        """Adds the image in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addImage(image,image_cord)
# ----------------------- #

# blitting.
    def lightBlit(self) -> None:
        '''Blits all the images in the layers, taking less perfomance.\n'''
        for layer in self.layers:
            layer.blitNotOffsetWise()

    def blit(self) -> None:
        '''Blits all the images in the layers.\n'''
        for layer in self.layers: layer.blit(self.camera.getPos())
# ---------------- #

# update.
    def reset(self) -> None:
        """Clears all images in the layer.\n"""
        for layer in self.layers:
            layer.reset()

    def lightUpdate(self) -> None:
        '''Updates instance without handling Camera.\n'''
        self.lightBlit()
        self.reset()

        pg.display.update()

    def update(self, dt: float, player_center: pg.math.Vector2) -> None:        
        '''Updates the instance handling Camera.\n'''
        self.blit()
        self.reset()

        self.camera.update(dt, player_center)
        pg.display.update()