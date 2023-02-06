class Stats():
    def __init__(self, max_life: float, max_mana: float, max_stamina: float) -> None:

        self.max_life = max_life
        self.life = self.max_life

        self.max_mana = max_mana
        self.mana = self.max_mana

        self.max_stamina = max_stamina
        self.stamina = self.max_stamina

        self.regen_factor = 2

        # booleans.
        self.is_taking_damage = False
        self.is_dying = False

    def setRegenFactor(self, value: float) -> None:
        self.regen_factor = value

    def regen(self, dt: float) -> None:
        '''Regens all the atributes with regen_factor base.\n'''
        if not self.is_taking_damage:
            if self.life + (self.regen_factor*dt) <= self.max_life: self.life += self.regen_factor*dt
            else: self.life = self.max_life

        if self.mana + (self.regen_factor*1.4*dt) <= self.max_mana: self.max_mana += self.regen_factor*1.4*dt
        else: self.mana = self.max_mana

        if self.stamina + (self.regen_factor*2*dt) <= self.max_stamina: self.stamina += self.regen_factor*2*dt
        else: self.stamina = self.max_stamina

    def spend(self, dt: float, qnt: float, which: int) -> None:
        '''Spends the instance atributte by the given quantity according to delta time.\n
           1->life, 2->mana, 3->stamina.\n'''
           
        if which == 1:
            self.is_taking_damage = True
            self.life -= (qnt*dt)

            if self.life <= 0:
                self.is_dying = True
                self.life = 0
            
            return

        if which == 2:
            self.mana -= qnt*dt

            if self.mana <= 0: self.mana = 0
            
            return

        if which == 3:
            self.stamina -= qnt*dt

            if self.stamina <= 0: self.stamina = 0

            return

    def update(self, dt: float) -> bool:
        '''Regenerates the atributes.\n
           Returns false if the instance is dead.\n'''
        if self.is_dying: return True
        
        self.regen(dt)
        self.is_taking_damage = False

        return False