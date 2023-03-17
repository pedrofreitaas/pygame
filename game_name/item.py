from game_name.entities.entity import *

class Item():
    # exceptions.
    class itemAlredyHasHolder(ValueError): pass
    class itemCantBeGivenToNonEntity(ValueError): pass
    # --------------------------- #

    #
    @classmethod
    def infoCode(cls: 'Item') -> str:
        return 'item'
    #

    def __init__(self, holder: Entity) -> None:
        if not isinstance(holder, Entity): raise ValueError
        self._holder: None|Entity = None
        self.holder = holder

    #
    @property
    def holder(self) -> None:
        return self._holder
    
    @holder.setter
    def holder(self, newHolder: Entity) -> None:
        '''Sets the item to be hold by an entity.\n
           * can throw itemAlredyHasHolder.\n
           * can throw itemCantBeGivenToNonEntity.\n'''
        if not isinstance(newHolder, Entity): raise Item.itemCantBeGivenToNonEntity
        
        if self._holder != None: raise Item.itemAlredyHasHolder

        self._holder = newHolder

    @holder.getter
    def holder(self) -> Entity:
        return self._holder
    #

    def give(self, newHolder: Entity) -> bool:
        '''Sets the holder of the item to newHolder.\n
           If the set was succesfull, return true.\n'''

        try: 
            self.holder = newHolder
            return True
        except Item.itemAlredyHasHolder:
            if isinstance(newHolder, Entity): 
                self._holder = newHolder
                return True
        except ...: return False