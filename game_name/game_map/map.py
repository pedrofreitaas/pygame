from pytmx import load_pygame, TiledMap
import pygame as pg
from game_name.game_map.structure import *
import blitter as blt
from time import time as tm

class Map():
    blitter: blt.Blitter = 0

    def __init__(self, blitter: blt.Blitter) -> None:
        if Map.blitter != 0: raise ValueError

        Map.blitter = blitter

        tmx: TiledMap = load_pygame('assets/map/map.tmx')
        Map.blitter.setCameraMapSize( [tmx.width*tmx.tilewidth, tmx.height*tmx.tileheight] )

        self.map_layer_matrices: list[list[list[Structure]]] = []
        
        for layer_idx in range(len(tmx.layers)):
            self.map_layer_matrices.append([])

            for i in range(tmx.height):
                self.map_layer_matrices[layer_idx].append([])

                for j in range(tmx.width):
                    self.map_layer_matrices[layer_idx][i].append(None)

            for x,y, surf in tmx.layers[layer_idx].tiles():
                self.map_layer_matrices[layer_idx][x][y] = Structure(pg.math.Vector2(x,y), surf, tmx.get_tile_properties(x,y,layer_idx))
                            
    def getStructuresInRect(self, layer_idx: int, rect: pg.rect.Rect, radius=[50,50] ) -> list[Structure]:
        '''Returns all the structures that are in the rect and in the layer.\n
           Radius parameter inflates the rect.\n'''
        structs = []

        rect.inflate_ip(radius)

        initial_grid = [(rect.left - rect.left%32)/32, (rect.top - rect.top%32)/32]
        final_grid = [(rect.right + (32-rect.right%32))/32, (rect.bottom + (32-rect.bottom%32))/32]

        # surf = pg.surface.Surface((32*(final_grid[0]-initial_grid[0]),32*(final_grid[1]-initial_grid[1])))
        # Map.blitter.addImageInLayer(3, surf, (initial_grid[0]*32, initial_grid[1]*32))

        for x in range(int(initial_grid[0]), int(final_grid[0])):
            for y in range(int(initial_grid[1]), int(final_grid[1])):
                if self.map_layer_matrices[layer_idx][x][y] != None:
                    structs.append(self.map_layer_matrices[layer_idx][x][y])

        return structs

    def getStructuresInLayerDisplay(self, layer_idx: int) -> None:
        '''Fills the parameter list with all the structures than are contained in the display according to camera offeset.\n
           It helps by disconsidering structures that are not in the display, and must not impact in the game.\n'''
        structs = []
        return []

        gridStart = -Map.blitter.camera.pos / 32
        gridStart = gridStart - pg.math.Vector2(2,2)

        gridEnd = gridStart + pg.math.Vector2(39, 24)

        count=0         
        for struct in self.layers[layer_idx]:
                if count > 936: break
                
                if struct.grid[0] < gridStart[0]: continue
                elif struct.grid[0] > gridEnd[0]: continue
                
                if struct.grid[1] < gridStart[1]: continue
                elif struct.grid[1] > gridEnd[1]: continue

                structs.append(struct)
                count += 1

        return structs

    def blit(self) -> None:
        '''Blits all the structures.\n'''

        gridStart = -Map.blitter.camera.pos / 32
        gridStart = gridStart - pg.math.Vector2(2,2)

        gridEnd = gridStart + pg.math.Vector2(39, 24)

        for layer_idx in range(len(self.map_layer_matrices)-1):            
            for x in range(int(gridStart[0]), int(gridEnd[0])):
                for y in range(int(gridStart[1]), int(gridEnd[1])):

                    if self.map_layer_matrices[layer_idx][x][y] == None: continue

                    pos = pg.math.Vector2(x,y) * 32
                    image = self.map_layer_matrices[layer_idx][x][y].image

                    Map.blitter.addImageInLayer(layer_idx, image, pos)

    def update(self) -> None:
        self.blit()

        self.previous_offset = -Map.blitter.camera.pos