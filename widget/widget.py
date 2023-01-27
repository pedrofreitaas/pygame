import pygame as pg 

class Widget():
    id = 1
    widgets: list['Widget'] = []

    def deleteWidgets() -> None:
        '''Deletes all the class register widgets from internal class data.\n'''
        Widget.widgets.clear()

    def updateWidgets(events: list[pg.event.Event]) -> None:
        '''Updates all storaged widgets.\n'''

        for wid in Widget.widgets:
            wid.update(events)

    def __init__(self) -> None:
        '''Initializes a widget instance with a unique id, and appends it in the global widget list.\n'''
        
        self.id = Widget.id
        Widget.id += 1
        Widget.widgets.append(self)

    def __eq__(self, __o: object) -> bool:
        if self.id == __o.id:
            return True

        return False

    def kill(self) -> None:
        '''Removes the instance from the internal class data.\n
           Remember to remove from variables that was set outside of the class.\n'''

        Widget.widgets.remove(self)
        del self

