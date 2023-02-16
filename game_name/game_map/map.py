from pytmx import load_pygame, TiledMap, TiledTileLayer
import pygame as pg
from game_name.game_map.structure import *
import blitter as blt

class Layer():
    def __init__(self, tmx_layer: TiledTileLayer, tiles_numb: tuple[int,int], tile_size: tuple[int,int]) -> None:
        self.matrix: list[list[Structure]] = []
        self.tiles_numb: tuple[int,int] = tiles_numb
        self.tiles_size: tuple[int,int] = tile_size

        for i in range(self.tiles_numb[0]):
            self.matrix.append([])
            for j in range(self.tiles_numb[1]):
                self.matrix[i].append(None)

        for x, y, surf in tmx_layer.tiles():
            try: self.matrix[x][y] = Structure(pg.math.Vector2(x,y), surf, tmx_layer.data[y][x])
            except IndexError: pass
        
    def getMapSize(self) -> tuple[int,int]:
        return [self.tiles_size[0]*self.tiles_numb[0], self.tiles_size[1]*self.tiles_numb[1]]
    
    def getStructuresInRect(self, rect: pg.rect.Rect, radius: pg.math.Vector2 ) -> list[Structure]:
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

                try:
                    if self.matrix[x][y] != None:
                        structs.append(self.matrix[x][y])

                except IndexError: pass

        return structs

class Map():
    def __init__(self, blitter: blt.Blitter) -> None:
        tmx: TiledMap = load_pygame('assets/map/map.tmx')

        blitter.camera.setMapSize( [tmx.width*tmx.tilewidth, tmx.height*tmx.tileheight] )

        self.layers: list[Layer] = []
        
        for layer in tmx: self.layers.append(Layer(layer, [tmx.width, tmx.height], [tmx.tilewidth, tmx.tileheight]))

    def getStructuresInRectInLayer(self, layer_idx: int, rect: pg.rect.Rect, radius: pg.math.Vector2) -> list[Structure]:
        return self.layers[layer_idx].getStructuresInRect(rect,radius)

    def blit(self, blitter: blt.Blitter) -> None:
        '''Blits all the structures.\n
           For every tile that is blitted, updates the id stored in lastTileIDs in that position.\n
           Check if the current ID in lastTileIDs isn't equal to the one that is going to be blitted, to avoid rebliting the same tiles.\n'''
        
        for idx, layer in enumerate(self.layers):
            for struct in layer.getStructuresInRect(blitter.camera.getCaptureRect(), [0,0]):
                blitter.addImage(idx, struct.image, struct.getPos())

    def update(self, blitter: blt.Blitter) -> None:
        self.blit(blitter)
    