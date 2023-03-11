import pygame as pg
from timer import *
from time import time as tm
import sys

pg.init()
pg.font.init()
pg.mixer.init(1000, 0, 16, 2048)

#Display.
flags = pg.SCALED | pg.DOUBLEBUF
sizeDisplay = [1120, 630]
screen = pg.display.set_mode( (sizeDisplay[0],sizeDisplay[1]), flags )

#importing entities.
import game_name.entities.player.player as pl

import game_name.entities.enemies.water_priestess.water_priestess as wtr_priest
wtr_priest.handleJson()

import game_name.entities.enemies.ronin.ronin as ronin
ronin.handleJson()

import game_name.entities.enemies.earth_monk.earth_monk as earth_monk
earth_monk.handleJson()

import game_name.entities.enemies.forest_wolf.forest_wolf as frst_wolf
frst_wolf.handleJson()
# ------------------------- #

import blitter as blt
import widget.button as button
from game_name.game_map.map import *

previous = tm()
def getDt() -> float:
    '''Gets time passed since the last dt update.\n'''
    global previous

    dt = tm() - previous
    previous = tm()

    return dt

class Game():
    display = screen
    fonts: list[pg.font.Font] = [pg.font.Font('assets/font/PeaberryBase.ttf', 12),
                                 pg.font.Font('assets/font/PeaberryBase.ttf', 16),
                                 pg.font.Font('assets/font/PeaberryBase.ttf', 20),
                                 pg.font.Font('assets/font/PeaberryBase.ttf', 24),
                                 pg.font.Font('assets/font/PeaberryBase.ttf', 28)]
    game_music = pg.mixer.Sound('assets/game/sounds/Celestial.mp3')
    game_music.set_volume(0.05)

    def __init__(self) -> None:
        #dt
        self.dt = getDt()
        
        #booleans
        self.playing: bool = True
        self.paused: bool = False
        self.blit_minimap: bool = False

        self.events: list[pg.event.Event] = []

        self.blitter: blt.Blitter = blt.Blitter(Game.display, 5)
        self.blitter.changeLayerCameraSensibility(self.blitter.lastLayer(), False)
        pl.ent.Entity.blitter = self.blitter

        self.clock: pg.time.Clock = pg.time.Clock()

        self.map: Map = Map(self.blitter)
        pl.ent.Entity.map: Map = self.map

        self.game_timers: list[Timer] = []

        self.player = pl.handleJson()
        self.previous_player_pos = self.player.pos

        self.dtSurface = self.fonts[2].render(str(round(self.dt,4)), 1, pg.Color("black"))
        self.fpsSurface = self.fonts[2].render(str(round(0)), 1, (0,0,0))
    
        self.dtSurface_blitPOS = pg.math.Vector2( self.blitter.displaySize()[0]-self.dtSurface.get_size()[0]-20,10 )
        self.fpsSurface_blit_pos = pg.math.Vector2( self.blitter.displaySize()[0]-self.dtSurface.get_size()[0]-20,10+self.dtSurface.get_size()[1]+10 )

        self.game_timers.append(Timer(1, lambda: self.updateDtSurface(),-1))

        Game.game_music.play(-1)

    def updateDtSurface(self) -> None:
        '''Updates the dt surface with the most recent value.\n'''
        self.dtSurface = self.fonts[2].render(str(round(self.dt,4)), 1, (0,0,0))
        self.fpsSurface = self.fonts[2].render(str(self.clock.get_fps()), 1, (0,0,0))

    def getEvents(self) -> None:
        '''Gets the loop events and save them in a self.variable.\n'''

        self.events = pg.event.get()

    def treatEvents(self) -> None:
        '''Gets and treats loop events.\n'''

        self.getEvents()

        for event in self.events:

            if event.type == pg.QUIT:
                self.playing = False

            if event.type == pg.KEYDOWN: 
                if event.key == pg.K_ESCAPE:
                    self.paused = not self.paused

                if event.key == pg.K_F11:
                    pg.display.toggle_fullscreen()

                if event.key == 109:
                    self.blit_minimap = not self.blit_minimap

                if event.key == pg.K_LCTRL:
                    self.blitter.camera.UNlock()

    def UNpause(self) -> None:
        '''Pauses or unpauses the game, depending on the current value of self.paused.\n'''
        self.paused = not self.paused

    def updateDt(self) -> None:
        '''Updates the delta time in all instances.\n'''

        self.dt = getDt()
        pl.ent.Entity.dt = self.dt

        #if self.dt > 0.05: print('dt problem.\n')

    def pauseloop(self) -> None:
        pl.ent.pauseTimers(throw=False)
        
        unpauseButton = button.Button(pg.math.Vector2(500,500), lambda: self.UNpause(), 'unpause', Game.fonts[3], pg.color.Color('black'), True)
        
        while self.paused:
            if not self.playing: break

            self.treatEvents()

            unpauseButton.update(self.blitter, self.events)

            self.blitter.lightUpdate()

        pl.ent.unpauseTimers(throw=False)
        self.updateDt()

    def blitDt(self) -> None:
        '''Updates and blits delta time.\n'''
        self.updateDt()
        self.blitter.addImage(self.blitter.lastLayer(), self.dtSurface, self.dtSurface_blitPOS)
        self.blitter.addImage(self.blitter.lastLayer(), self.fpsSurface, self.fpsSurface_blit_pos)

    def gameloop(self) -> None:
        while self.playing:

            if self.paused:
                self.pauseloop()
            
            self.blitDt()
            
            self.treatEvents()

            self.player.update(self.events)
            pl.ent.updateEnemies()
            
            self.map.update(self.blitter, self.dt)

            updateTimers(self.game_timers)

            if self.blit_minimap: pl.ent.blitMinimap(self.fonts[3])

            self.blitter.update(self.dt, self.player.center())