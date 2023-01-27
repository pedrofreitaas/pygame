import widget.widget as wd
import blitter as blt

class Button(wd.Widget):

    def __init__(self, pos: wd.pg.math.Vector2, procedure: callable, txt: str, font: wd.pg.font.Font, color: wd.pg.color.Color, once=True) -> None:
        '''Once: if true the button will be deleted after it's clicked.\n'''

        super().__init__()

        self.once: bool = once

        self.text: str = txt
        self.pos: wd.pg.math.Vector2 = pos
        self.procedure: callable = procedure

        self.font: wd.pg.font.Font = font
        self.font_color: wd.pg.color.Color = color

        self.rect: wd.pg.rect.Rect = self.getTextSurface().get_rect().move(self.pos)

    def setPos(self, pos: wd.pg.math.Vector2) -> None:
        self.pos = pos

    def getTextSurface(self) -> wd.pg.surface.Surface:
        return self.font.render(self.text, 1, self.font_color)
    
    def getTextSurfaceSize(self) -> wd.pg.math.Vector2:
        return wd.pg.math.Vector2(self.getTextSurface().get_size())

    def blit(self, blitter: blt.Blitter, layer: int) -> None:
        '''Blits the button using a blitter instance.\n'''
        blitter.addImageInLayer(layer, self.getTextSurface(), self.pos)

    def update(self, events: list[wd.pg.event.Event]) -> None:
        self.rect = self.getTextSurface().get_rect().move(self.pos)

        for event in events:
            if event.type == wd.pg.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                self.procedure()
                if self.once: self.kill()
