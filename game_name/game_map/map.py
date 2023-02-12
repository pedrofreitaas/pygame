from pytmx import load_pygame, TiledMap, TiledTileLayer
import pygame as pg
from game_name.game_map.structure import *
import blitter as blt
from time import time as tm

class Layer():
    def __init__(self, tmx_layer: TiledTileLayer, tmx_size: tuple[int,int]) -> None:
        self.matrix: list[list[Structure]] = []

        for i in range(tmx_size[0]):
            self.matrix.append([])
            for j in range(tmx_size[1]):
                self.matrix[i].append(None)

        for x, y, surf in tmx_layer.tiles():
            self.matrix[x][y] = Structure(pg.math.Vector2(x,y), surf, tmx_layer.data[x][y])

    def getStructuresInRect(self, rect: pg.rect.Rect, radius=[50,50] ) -> list[Structure]:
        '''Returns all the structures that are in the rect and in the layer.\n
           Radius parameter inflates the rect.\n'''
        structs = []

        rect.inflate(radius)

        initial_grid = [(rect.left - rect.left%32)/32, (rect.top - rect.top%32)/32]
        final_grid = [(rect.right + (32-rect.right%32))/32, (rect.bottom + (32-rect.bottom%32))/32]

        # surf = pg.surface.Surface((32*(final_grid[0]-initial_grid[0]),32*(final_grid[1]-initial_grid[1])))
        # Map.blitter.addImageInLayer(3, surf, (initial_grid[0]*32, initial_grid[1]*32))

        for x in range(int(initial_grid[0]), int(final_grid[0])):
            for y in range(int(initial_grid[1]), int(final_grid[1])):
                if self.matrix[x][y] != None:
                    structs.append(self.matrix[x][y])

        return structs

class Map():
    def __init__(self, blitter: blt.Blitter) -> None:
        tmx: TiledMap = load_pygame('assets/map/map.tmx')
        blitter.setCameraMapSize( [tmx.width*tmx.tilewidth, tmx.height*tmx.tileheight] )

        self.layers: list[Layer] = []
        
        for layer in tmx:
            self.layers.append(Layer(layer, [tmx.width, tmx.height]))

    def getStructuresInRectInLayer(self, layer_idx: int, rect: pg.rect.Rect, radius=[50,50]) -> list[pg.rect.Rect]:
        return self.layers[layer_idx].getStructuresInRect(rect,radius=radius)

    def blit(self, blitter: blt.Blitter) -> None:
        '''Blits all the structures.\n'''

        displayRect = pg.rect.Rect(-blitter.camera.pos, blitter.displaySize()) 

        for idx, layer in enumerate(self.layers): 
            for struct in layer.getStructuresInRect(displayRect, radius=[64,64]):
                    blitter.addImageInLayer(idx, struct.image, struct.getPos(), struct.id)

    def update(self, blitter: blt.Blitter) -> None:
        self.blit(blitter)