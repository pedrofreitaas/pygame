from pytmx import load_pygame, TiledMap
import pygame as pg
from game_name.game_map.structure import *
import blitter as blt

class Map():
    blitter: blt.Blitter = 0

    def __init__(self, blitter: blt.Blitter) -> None:
        if Map.blitter != 0: raise ValueError

        Map.blitter = blitter

        tmx: TiledMap = load_pygame('assets/map/map.tmx')

        self.layers: list[list[Structure]] = []
        self.table: dict[str, Structure] = {}

        for idx, layer in enumerate(tmx.layers):
            self.layers.append([])

            for x,y, surf in layer.tiles():
                # dict.
                key = str(idx)+','+str(x)+','+str(y)
                self.table[key] = Structure(pg.math.Vector2(x,y), surf, tmx.get_tile_properties(x,y,idx) )
                
                # list.
                self.layers[idx].append( self.table[key] )

            self.layers[idx].sort(key= lambda x: x.grid.length_squared() )

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
                key = str(layer_idx)+','+str(x)+','+str(y)

                try: structs.append(self.table[key])
                except: pass

        return structs

    def getStructuresInLayerDisplay(self, layer_idx: int) -> None:
        '''Fills the parameter list with all the structures than are contained in the display according to camera offeset.\n
           It helps by disconsidering structures that are not in the display, and must not impact in the game.\n'''

        structs = []

        gridStart = Map.blitter.cameraOffset() / 32
        gridEnd = gridStart + pg.math.Vector2(35, 20)

        count=0         
        for struct in self.layers[layer_idx]:
                if count > 751: break
                
                if struct.grid[0] < gridStart[0]: continue
                elif struct.grid[0] > gridEnd[0]: continue
                
                if struct.grid[1] < gridStart[1]: continue
                elif struct.grid[1] > gridEnd[1]: continue

                structs.append(struct)
                count += 1

        return structs

    def blit(self) -> None:
        '''Blits all the structures.\n'''

        for layer_idx in range(0, len(self.layers)-1):  
            structs: list[Structure] = self.getStructuresInLayerDisplay(layer_idx)   
            
            for struct in structs:
                # surf = pg.surface.Surface((struct.getRect().width, struct.getRect().height))
                # Map.blitter.addImageInLayer(layer_idx, surf, struct.getRect().topleft)

                Map.blitter.addImageInLayer(layer_idx, struct.image, struct.getPos())
    
    def update(self) -> None:
        self.blit()