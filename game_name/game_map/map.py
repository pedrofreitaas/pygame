from pytmx import load_pygame
import pygame as pg
from game_name.game_map.structure import *
import blitter as blt

class Map():
    blitter: blt.Blitter = 0

    def __init__(self, blitter: blt.Blitter) -> None:
        if Map.blitter != 0: raise ValueError

        Map.blitter = blitter

        tmx = load_pygame('assets/map/map.tmx')

        self.layers: list[list[Structure]] = []

        for idx, layer in enumerate(tmx.layers):
            self.layers.append([])

            for x,y, surf in layer.tiles():
                self.layers[idx].append( Structure(pg.math.Vector2(x,y), surf) )

            self.layers[idx].sort(key= lambda x: x.grid.length_squared() )

    def blit(self) -> None:
        '''Blits all the structures.\n'''

        gridStart = Map.blitter.cameraOffset() / 32
        gridEnd = gridStart + pg.math.Vector2(35, 20)

        for idx, layer in enumerate(self.layers):
            count=0         
            for struct in layer:
                if count > 751: break
                
                if struct.grid[0] < gridStart[0]: continue
                elif struct.grid[0] > gridEnd[0]: continue
                
                if struct.grid[1] < gridStart[1]: continue
                elif struct.grid[1] > gridEnd[1]: continue

                Map.blitter.addImageInLayer(idx, struct.image, struct.getPos())
                count += 1

    def update(self) -> None:
        self.blit()