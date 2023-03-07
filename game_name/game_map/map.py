from pytmx import load_pygame, TiledMap, TiledTileLayer, TiledObjectGroup, TiledObject
import pygame as pg
from game_name.game_map.structure import *
from game_name.game_map.object import *
import blitter as blt
from math import ceil

class Layer():
    def __init__(self, tmx_layer: TiledTileLayer, tiles_numb: tuple[int,int], tile_size: tuple[int,int]) -> None:
        if not isinstance(tmx_layer, TiledTileLayer): raise ValueError

        self.matrix: list[list[ Structure ]] = []
        self.tiles_numb: tuple[int,int] = tiles_numb
        self.tiles_size: tuple[int,int] = tile_size

        for i in range(self.tiles_numb[0]):
            self.matrix.append([])
            for j in range(self.tiles_numb[1]):
                self.matrix[i].append(None)

        for x, y, surf in tmx_layer.tiles():
            try: 
                self.matrix[x][y] = Structure(pg.math.Vector2(x,y), surf, tmx_layer.data[y][x])
            except IndexError: pass      
    
    def getMapSize(self) -> tuple[int,int]:
        return [self.tiles_size[0]*self.tiles_numb[0], self.tiles_size[1]*self.tiles_numb[1]]

    def getStructuresInRect(self, rect: pg.rect.Rect, radius: pg.math.Vector2) -> list[Structure]:
        '''Returns all the structures that are in the rect and in the layer.\n
           Radius parameter inflates the rect.\n'''
        structs: list[Structure] = []

        rect.inflate(radius)

        initial_grid = [int(rect.left/32), int(rect.top/32)]
        final_grid = [ceil(rect.right/32), ceil(rect.bottom/32)]

        for x in range(int(initial_grid[0]), int(final_grid[0])):
            for y in range(int(initial_grid[1]), int(final_grid[1])):

                try:
                    if self.matrix[x][y] != None: structs.append(self.matrix[x][y])
                except IndexError: pass

        return structs

class Map():
    def __init__(self, blitter: blt.Blitter) -> None:
        tmx: TiledMap = load_pygame('assets/map/map.tmx')

        blitter.camera.setMapSize( [tmx.width*tmx.tilewidth, tmx.height*tmx.tileheight] )

        self.layers: list[Layer] = []
        self.objects: list[Object] = []

        self.map_size: tuple[float,float] = [tmx.width*tmx.tilewidth, tmx.height*tmx.tileheight]
        
        for layer in tmx: 
            if isinstance(layer, TiledTileLayer): 
                self.layers.append(Layer(layer, [tmx.width, tmx.height], [tmx.tilewidth, tmx.tileheight]))
            
            elif isinstance(layer, TiledObjectGroup):
                for obj in layer: self.objects.append( Object(obj) )

        self.miniature: pg.surface.Surface = pg.surface.Surface(self.map_size).convert()
        self.miniature.set_colorkey((0,0,0))
        self.scale_vec: pg.math.Vector2 = pg.math.Vector2(0,0)
        self.miniature_size: tuple[float,float] = (600,600)

        self.createMiniature()

#
    def structExists(self, rect: pg.rect.Rect, layer: int=0) -> bool:
        '''Returns true if there is a structure in the parameter rect.\n
           Starts the search from the layer parameter, with default value zero.\n'''

        for layerInd in range(layer, len(self.layers) ):
            if len(self.layers[layerInd].getStructuresInRect(rect, (0,0))) > 0: return True

        return False
#
   
    def createMiniature(self) -> None:
        '''Blits the current state of the map into a miniature.\n'''
        for layer in self.layers:
            for structures in layer.matrix:
                for struct in structures:
                    if struct == None: continue
                    self.miniature.blit( struct.image, struct.getPos() )

        self.miniature = pg.transform.scale(self.miniature, self.miniature_size)
        self.scale_vec: pg.math.Vector2 = pg.math.Vector2(self.miniature_size[0]/self.map_size[0],self.miniature_size[1]/self.map_size[1])
        
        background = pg.surface.Surface((self.miniature_size[0]+10, self.miniature_size[1]+10)).convert()
        background.blit(self.miniature, (5,5))

        self.miniature = background

#
    def getStructuresInRectInLayer(self, layer_idx: int, rect: pg.rect.Rect, radius: pg.math.Vector2) -> list[Structure]:
        return self.layers[layer_idx].getStructuresInRect(rect,radius)
#

    def blit(self, blitter: blt.Blitter) -> None:
        '''Blits all the elements.\n'''
        
        captureRect = blitter.camera.getCaptureRect()
        for idx, layer in enumerate(self.layers):
            for struct in layer.getStructuresInRect(captureRect, [0,0]):
                blitter.addImage(idx, struct.image, struct.getPos())

        for obj in self.objects:
            if captureRect.collidepoint( obj.pos ): obj.blit(blitter)

    def update(self, blitter: blt.Blitter, dt: float) -> None:
        self.blit(blitter)
        updateObjs(dt)
    