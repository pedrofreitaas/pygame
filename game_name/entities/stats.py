class Stats():
    def __init__(self, max_life: float, max_mana: float, max_stamina: float) -> None:

        self.max_life = max_life
        self.life = self.max_life
        self.previous_life = self.life

        self.max_mana = max_mana
        self.mana = self.max_mana
        self.previous_mana = self.mana

        self.max_stamina = max_stamina
        self.stamina = self.max_stamina
        self.previous_stamina = self.stamina

        self.life_regen_factor = 2
        self.mana_regen_factor = 1.4
        self.stamina_regen_factor = 2.3

        # booleans.
        self.is_taking_damage = False
        self.is_using_mana = False
        self.is_using_stamina = False
        self.is_dying = False

    def setRegenFactor(self, value: float, which: int=1) -> None:
        '''Changes the stat regeneration to the value paremeter.\n
           which: 1->life, 2->mana, 3->stamina.\n'''
        if which == 1: self.life_regen_factor = value
        elif which == 2: self.mana_regen_factor = value
        elif which == 3: self.stamina_regen_factor = value

    def regen(self, dt: float) -> None:
        '''Regens all the atributes with (stat)_regen_factor base.\n'''
        if not self.is_taking_damage:
            self.life += self.life_regen_factor*dt
            if self.life > self.max_life: self.life = self.max_life

        if not self.is_using_mana:
            self.mana += self.mana_regen_factor*dt
            if self.mana > self.max_mana: self.mana = self.max_mana

        if not self.is_using_stamina:
            self.stamina += self.stamina_regen_factor*dt
            if self.stamina > self.max_stamina: self.stamina = self.max_stamina

    def hasEnough(self, qnt: float, which: int) -> bool:
        '''Returns true if the instance has the according stat in the parameter quantity.\n
           which: 1->life, 2->mana, 3->stamina.\n'''

        if which == 1:
            if self.life >= qnt: return True
            return False

        if which == 2:
            if self.mana >= qnt: return True
            return False

        if which == 3:
            if self.stamina >= qnt: return True
            return False

    def spend(self, dt: float, qnt: float, which: int) -> None:
        '''Spends the instance atributte by the given quantity according to delta time.\n
           1->life, 2->mana, 3->stamina.\n'''
           
        if which == 1:
            self.life -= (qnt*dt)

            if self.life <= 0:
                self.is_dying = True
                self.life = 0
            
            return

        if which == 2:
            self.mana -= qnt*dt

            if self.mana < 0: self.mana = 0
            
            return

        if which == 3:
            self.stamina -= qnt*dt

            if self.stamina < 0: self.stamina = 0

            return
    
    def add(self, dt: float, qnt: float, which: int) -> None:
        '''Adds the instance atributte by the given quantity according to delta time.\n
            1->life, 2->mana, 3->stamina.\n'''
           
        if which == 1:
            self.life += (qnt*dt)
            if self.life > self.max_life:
                self.life = self.max_life
            
            return

        if which == 2:
            self.mana += qnt*dt
            if self.mana > self.max_mana: self.mana = self.max_mana
            
            return

        if which == 3:
            self.stamina += qnt*dt
            if self.stamina > self.max_stamina: self.stamina = self.max_stamina

            return

    def getPercentage(self, which: int) -> float:
        '''Returns the percentage of the corresponde which parameter stat.\n
           which -> 1=life, 2=mana, 3=stamina.\n'''
        if which == 1: return self.life/self.max_life
        elif which == 2: return self.mana/self.max_mana
        elif which == 3: return self.stamina/self.max_stamina
        
    def checkStats(self) -> bool:
        '''Checks if the entity is taking damage.\n'''
        #life
        self.is_taking_damage = self.life < self.previous_life
        self.previous_life = self.life

        #mana
        self.is_using_mana = self.mana < self.previous_mana
        self.previous_mana = self.mana
        
        #stamina
        self.is_using_stamina = self.stamina < self.previous_stamina
        self.previous_stamina = self.stamina

    def update(self, dt: float) -> bool:
        '''Regenerates the atributes.\n
           Returns false if the instance is dead.\n'''
        if self.is_dying: return False
        
        self.checkStats()
        self.regen(dt)

        return True