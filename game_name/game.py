import pygame as pg
import blitter as blt
import widget.button as button
from timer import *
from time import time as tm

pg.init()
pg.font.init()
pg.mixer.init(1000, 0, 16, 2048)

#Display.
sizeDisplay = [1120, 630]
screen = pg.display.set_mode( (sizeDisplay[0],sizeDisplay[1]) )

#importing entities.
import game_name.entities.player.player as pl
import game_name.entities.enemies.water_priestess.water_priestess as wtr_priest

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

    def __init__(self) -> None:

        #dt
        self.dt = getDt()
        
        #booleans
        self.playing: bool = True
        self.paused: bool = False

        self.events: list[pg.event.Event] = []

        self.blitter: blt.Blitter = blt.Blitter(Game.display, 5)
        pl.ent.Entity.blitter = self.blitter

        self.clock: pg.time.Clock = pg.time.Clock()

        self.game_timers: list[Timer] = []
        self.player = pl.Player(pg.math.Vector2(20,20))

        self.enemy = wtr_priest.WaterPriestess(pg.math.Vector2(200,400), 1)

    def getEvents(self) -> None:
        '''Gets the loop events and save them in a self.variable.\n'''

        self.events = pg.event.get()

    def treatEvents(self) -> None:
        '''Gets and treats loop events.\n'''

        self.getEvents()

        for event in self.events:

            if event.type == pg.QUIT:
                self.playing = False

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.paused = not self.paused

    def UNpause(self) -> None:
        '''Pauses or unpauses the game, depending on the current value of self.paused.\n'''
        self.paused = not self.paused

    def updateDt(self) -> None:
        '''Updates the delta time in all instances.\n'''

        self.dt = getDt()
        pl.ent.Entity.dt = self.dt

        if self.dt > 0.2: print('dt problem.\n')

    def pauseloop(self) -> None:
        pl.ent.pauseTimers(throw=False)
        
        unpauseButton = button.Button(pg.math.Vector2(500,500), lambda: self.UNpause(), 'unpause', Game.fonts[0], pg.color.Color('black'), True)
        
        while self.paused:
            
            self.treatEvents()

            unpauseButton.update(self.events)

            unpauseButton.blit(self.blitter, 1)

            self.blitter.update(pg.math.Vector2())

        pl.ent.unpauseTimers(throw=False)

    def blitDt(self) -> None:
        dtSurface = self.fonts[2].render(str(round(self.dt,4)), 1, pg.Color("coral"))
        blitPOS = [self.blitter.displaySize()[0]-dtSurface.get_size()[0]-10,10]

        self.blitter.addImageInLayer(self.blitter.lastLayer(), dtSurface, blitPOS)

    def gameloop(self) -> None:
        while self.playing:

            if self.paused:
                self.pauseloop()

            self.updateDt()
            
            self.blitDt()
            
            self.treatEvents()

            self.player.update(self.events)
            pl.ent.updateEnemies()

            self.blitter.update(pg.math.Vector2())
            
            self.clock.tick(500)
