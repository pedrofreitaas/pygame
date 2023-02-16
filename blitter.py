import pygame as pg
from timer import *
from math import ceil

class TileIDS():
    def __init__(self, tiles_size: tuple[float,float], displayRect: pg.rect.Rect) -> None:
        self.tiles_size: tuple[int,int] = tiles_size

        final_grid = [ceil(displayRect.width/tiles_size[0]), ceil(displayRect.height/tiles_size[1])]

        self.tiles: list[list[int|None]] = []

        for x in range(final_grid[0]):
            self.tiles.append([])
            for y in range(final_grid[1]):
                self.tiles[x].append(None)

    def grid(self, pos: pg.math.Vector2|tuple[float,float]) -> tuple[int,int]:
        '''Returns the matrix position of the pos parameter.\n'''
        return [ int(pos[0]/self.tiles_size[0]), int(pos[1]/self.tiles_size[1]) ]

    def getID(self, grid: tuple[int,int]) -> int|None:
        '''Returns the id stored in that position of the instance tile's matrix.\n
           If the grid does not exist in the matrix, returns None.\n'''
        try: return self.tiles[grid[0]][grid[1]]
        except IndexError: return None

    def setID(self, grid: tuple[int,int], ID: int|None) -> None:
        '''Sets the ID of the instance tile's matrix to be the parameter.\n
           If the grid doesn't exist in the matrix, does nothing.\n'''
        try: self.tiles[grid[0]][grid[1]] = ID
        except IndexError: pass

    def setIDWithRect(self, rect: pg.rect.Rect, ID: int|None) -> None:
        '''Updates the all the grids of the instance tile's matrix covered by the rect parameter\n
           to be the parameter ID.\n'''
        startGrid = self.grid(rect.topleft)

        grids_x = ceil( (rect.width+ rect.left%self.tiles_size[0])/self.tiles_size[0] )
        grids_y = ceil( (rect.height+ rect.top%self.tiles_size[1])/self.tiles_size[1] )

        for x in range(grids_x):
            for y in range(grids_y):
                try: self.tiles[x+startGrid[0]][y+startGrid[1]] = ID
                except IndexError: pass

    def blit(self, display: pg.surface.Surface) -> None:
        '''Blits the IDs according to their grids.\n
           Debugging purposes.\n'''
        
        font = pg.font.SysFont('arial',20)
        surf = pg.surface.Surface(self.tiles_size)
        surf.set_colorkey((0,0,0))
        
        for i in range(len(self.tiles)-1):
            for j in range(len(self.tiles[i])-1):
                pos = (i*self.tiles_size[0], j*self.tiles_size[1])

                if self.tiles[i][j] != None: display.blit(font.render(str(self.tiles[i][j]), True, (255,0,0)), pos)

                pg.draw.rect(display, (255,0,0), surf.get_rect().move(pos), 1)

class Camera():
    def __init__(self) -> None:
        self.dt: float = 0

        self.previous_player_center: pg.math.Vector2 = pg.math.Vector2(0,0)

        self.pos: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.speed_dir: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.speed_value: float = 20

        self.display_rect: pg.rect.Rect = pg.rect.Rect(pg.display.get_surface().get_rect())
        self.center_rect: pg.rect.Rect = self.display_rect.inflate(-400,-400)

        #map infos
        self.map_size: tuple[float,float] = []
    
    def setMapSize(self, map_size : tuple[float,float]) -> None:
        '''Sets the instance's map size with the given parameter.\n'''
        self.map_size = map_size

    def getPos(self) -> None:
        return self.pos.copy()

# movement.
    def getPlayerDeltaPos(self, player_center: pg.math.Vector2) -> pg.math.Vector2:
        '''Returns player delta pos.\n'''
        dp = player_center - self.previous_player_center
        self.previous_player_center = player_center

        return dp

    def fitInsideMap(self) -> None:
        '''Automatically fits the instance inside the map's limits.\n'''
        outXRigth = self.map_size[0] + self.pos[0]-self.display_rect.width
        outYBottom = self.map_size[1] + self.pos[1]-self.display_rect.height
        
        if self.pos[0] > 0: self.pos[0]-=self.pos[0]
        elif outXRigth < 0: self.pos[0]-=outXRigth
        
        if self.pos[1] > 0: self.pos[1]-=self.pos[1]
        elif outYBottom < 0: self.pos[1]-=outYBottom

    def getMovementSpeed(self) -> pg.math.Vector2:
        '''Gets the camera move speed.\n'''
        speed = pg.math.Vector2(0,0)

        if not self.center_rect.collidepoint(self.previous_player_center+self.pos):
            fitVector = self.previous_player_center-pg.math.Vector2(self.center_rect.center)+self.pos
            speed -= fitVector.normalize()*self.dt*self.speed_value*10

        return speed

    def move(self) -> None:
        """Moves the instance.\n"""
        self.pos = self.pos + self.getMovementSpeed()
        self.fitInsideMap()
# -------------- #

# camera Rects.
    def getCaptureRect(self) -> None:
        '''Returns the rect that represents the area of coordinates that is been displayed.\n'''
        return pg.rect.Rect( -self.pos, (self.display_rect.width, self.display_rect.height) )

    def getDisplayRect(self) -> pg.rect.Rect:
        return self.display_rect

    def fitsDisplayRect(self, rect: pg.rect.Rect) -> bool:
        '''Returns true if the rect dislocated by the offset is in the display.\n'''
        return self.display_rect.contains( rect.move(self.pos) )
# ------------------- #

    def update(self, dt: float, player_center: pg.math.Vector2) -> None:
        """Moves the camera, based on the speed/delta given.\n"""

        playerDP = self.getPlayerDeltaPos(player_center) 
        
        if playerDP != pg.math.Vector2(0,0): self.speed_dir = playerDP.normalize()
        else: self.speed_dir = playerDP

        self.dt = dt
        self.move()
    
class Layer():
    def __init__(self, display: pg.surface.Surface) -> None:
        self.non_tiles: list[tuple[pg.surface.Surface, pg.math.Vector2]] = []
        self.tiles: list[tuple[pg.surface.Surface, pg.math.Vector2, int]] = []
        
        self.is_camera_sensible: bool = True

        self.display: pg.surface.Surface = display

    def imageTotal(self) -> int:
        """Returns the amount of images of the instance."""
        return len(self.non_tiles)+len(self.tiles)
    
    def reset(self) -> None:
        """Resets the instance."""
        self.non_tiles.clear()
        self.tiles.clear()
    
# adding registers functions.
    def addNonTile(self, image: pg.surface.Surface, image_cord : pg.math.Vector2) -> None:
        """Appends the image with the cords info given, in this layer"""
        self.non_tiles.append((image,image_cord))

    def addTile(self, image: pg.surface.Surface, image_cord : pg.math.Vector2, tileID: int) -> None:
        """Appends the image with the cords info given, in this layer"""
        self.tiles.append((image,image_cord,tileID))
# ----------------------------- #

# blit functions.
    def blit(self, lastTileIDs: TileIDS, offset: pg.math.Vector2) -> None:
        if self.is_camera_sensible: self.blitOffsetWise(lastTileIDs, offset)
        else: self.blitNotOffsetWise(lastTileIDs)

    def blitOffsetWise(self, lastTileIDs: TileIDS, offset: pg.math.Vector2) -> None:
        '''Blits the layer's images counting the offset.\n'''
        
        for image, pos in self.non_tiles:
            pos = pos + offset
            self.display.blit(image,pos)

            lastTileIDs.setIDWithRect(image.get_rect().move(pos), None)

        offset[0] -= offset[0]%32
        offset[1] -= offset[1]%32

        for image, pos, tileID in self.tiles:
            pos = pos + offset

            if lastTileIDs.getID(lastTileIDs.grid(pos)) == tileID: continue

            self.display.blit(image,pos)

            lastTileIDs.setIDWithRect(image.get_rect().move(pos), tileID)

    def blitNotOffsetWise(self, lastTileIDs: TileIDS) -> None:
        '''Blits the instance's image without couting for offsets.\n'''
        for image, pos in self.non_tiles:
            self.display.blit(image,pos)

            lastTileIDs.setIDWithRect(image.get_rect().move(pos), None)

        for image, pos, tileID in self.tiles:
            if lastTileIDs.getID(lastTileIDs.grid(pos)) == tileID: continue

            self.display.blit(image,pos)

            lastTileIDs.setIDWithRect(image.get_rect().move(pos), tileID)

    def lightBlit(self) -> None:
        '''Blits the images without offset nor checking ids.\n'''
        for image in self.non_tiles:
            self.display.blit(image[0], image[1])

        for image in self.tiles:
            self.display.blit(image[0], image[1])

class Blitter():
    def __init__(self, display: pg.surface.Surface, total_layers: int) -> None:
        self.display: pg.surface.Surface = display
        self.display_rect: pg.rect.Rect = display.get_rect()
        self.camera: Camera = Camera()

        #higher layers are blitted on top of the lowers
        self.layers: list[Layer] = []

        #putting layers
        for i in range(total_layers): self.createLayer()

        self.lastTileIDs: TileIDS = TileIDS([32,32], self.display_rect.inflate(32,32))

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

    def addNonTile(self, layerIndex: int, image: pg.surface.Surface, image_cord: pg.math.Vector2) -> None:
        """Adds the image in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addNonTile(image,image_cord)

    def addTile(self, layerIndex: int, image: pg.surface.Surface, image_cord: pg.math.Vector2, tileID: int) -> None:
        """Adds the struct in the chosen layer, with the coordinates of the parameter.\n"""
        self.layers[layerIndex].addTile(image,image_cord,tileID)

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

    def blit(self) -> None:
        '''Blits all the images in the layers.\n'''
        for layer in self.layers: layer.blit(self.lastTileIDs, self.camera.getPos())

        #self.lastTileIDs.blit(self.display)
    
    def lightUpdate(self) -> None:
        '''Updates instance withou handling: Struct IDs, Camera.\n'''
        self.lightBlit()
        self.reset()

        pg.display.flip()

    def update(self, dt: float, player_center: pg.math.Vector2) -> None:        
        '''Updates the instance handling: Camera, Struct IDs.\n'''
        self.blit()
        self.reset()

        self.camera.update(dt, player_center)
        pg.display.update()