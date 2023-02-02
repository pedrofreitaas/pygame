from time import time as tm

class Timer():

    class pausedDeactivatedClock(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
    class unpausedDeactivatedClock(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
    class requestingTimeFromNotWorkingClock(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __eq__(self, __o: object) -> bool:
        if type(self) == type(__o) and self.id == __o.id:
            return True
        return False

    def __init__(self, howLong: float, procedure: callable, cycles: int = -1) -> None:
        '''Creates a timer instance.\n
           howLong: the amount of time for the timer.\n
           procedure: the method to be called after the timer completes a cycle.\n
           cycles: defines how many cycles the timer will have, if it's -1, timer won't stop cycling.\n'''

        self.trigger_time = tm()
        self.how_long = howLong
        self.procedure = procedure
        self.cycles = cycles

        self.activated = True
        self.destroyed = False
        self.paused = False

        #aux.
        self.time_spent_before_pause = 0

    def changeCycleTime(self, cycleTime: float, reset: bool = True) -> None:
        '''Changes the cycle time to the new value.\n
           Reset is true -> The instance's cycle will restart with the new setted time.\n
           Reset is false -> The instance's cycle will count considering the current time of the cycle.\n'''

        self.how_long = cycleTime

        if reset:
            self.trigger_time = tm()
    
    def timeLeft(self) -> float:
        '''Gets time to next cycle.\n
           Throws if clock is deactivated or destroyed.\n

           OBS:
           As this clock is not continuous, the only way to check if the cycle is concluded is calling the it's update procedure.\n
           But, because of perfomance limitations, it happens after distinct amount times that don't respect the timer cycle's time.\n
           Because of that, the timer can get to the following situation: Cycle time has alredy passed, but the instance hasn't been\n
           updated. At this specific moment, the timeLeft value would be negative, but it can't happen, so the function would return 0.\n'''
        
        if not self.activated or self.destroyed:
            raise Timer.requestingTimeFromNotWorkingClock

        timeLeft = self.how_long - (tm() - self.trigger_time)

        if timeLeft < 0: return 0
        return timeLeft

    def discountCycle(self) -> None:
        '''Count's a cycle execution for the timer.\n'''
        if self.cycles == -1: return

        self.cycles = self.cycles - 1

        if self.cycles <= 0: self.destroyTimer()

    def destroyTimer(self) -> None:
        '''Timer will be destroyed and won't conclude any other cycle.\n'''
        self.destroyed = True

    def pause(self) -> None:
        '''Pauses the instance.\n
           Different from deactivation, when paused, a clock has to be unpaused by the unpause function.\n
           When unpaused, the timer will consider the time that past in the last cyle (before it was paused).\n
           Pausing a deactivated clock will throw.\n
           Pausing a paused clock will do nothing.\n'''

        if self.destroyed:
            return

        if not self.activated:
            raise Timer.pausedDeactivatedClock

        if self.paused:
            return 

        self.paused = True
        self.time_spent_before_pause = self.how_long - (tm() - self.trigger_time)

        if self.time_spent_before_pause <= 0:
            self.time_spent_before_pause = 0

    def unpause(self) -> None:
        '''Unpauses the instance.\n
           The instance will start counting from considering the time that alredy passed in the last cycle.\n
           Unpausing a deactivated clock will throw.\n
           Unpausing a not paused clock will do nothing.\n'''

        if self.destroyed:
            return

        if not self.activated:
            raise Timer.unpausedDeactivatedClock

        if not self.paused:
            return

        self.paused = False
        self.trigger_time = tm() - self.time_spent_before_pause

    def activateTimer(self) -> None:
        '''Timer will cycle again, reseted.\n
           Cycles's start time is set to the moment of the call.\n
           If the instance is paused, won't do anything.\n
           If instance is alredy active, does nothing.\n'''

        if self.destroyed:
            return

        if self.paused:
            return

        if self.activated:
            return

        self.activated = True
        self.trigger_time = tm()

    def deactiveTimer(self) -> None:
        '''Timer will be deactivated, so it won't take cycle.\n
           Different from pausing, won't considered the current passed time when it's activated again.\n
           If instance is paused, unpauses and deactivates.\n
           If instance alredy deactivated, does nothing.\n'''

        if self.destroyed:
            return

        if self.paused:
            self.unpause()

        if not self.activated:
            return

        self.activated = False

# list of timers procedures.
def unpauseTimers(timers: list[Timer]) -> None:
    '''Unpauses all the timers in the parameter.\n
       Won't throw under any circunstance.\n'''

    for timer in timers:
        try: timer.unpause()
        except Timer.unpausingNotPausedClock: pass
        except Timer.unpausingNotPausedClock: pass

def pauseTimers(timers: list[Timer]) -> None:
    '''Pauses all the timers in the list.\n
        Won't throw.\n'''

    for timer in timers:
        try: timer.pause()
        except Timer.pausedDeactivatedClock: pass

def updateTimers(timers: list[Timer]) -> None:
    '''Updates all the timers in the list.\n
       If the timer is destroyed, deletes the timer from the list in the next cycle.\n
       If it's paused or deactivated, does not complete any cycles.\n'''
    
    for index, timer in enumerate(timers):

        if timer.destroyed:
            del timers[index]
            continue

        if not timer.activated:
            continue

        if tm() - timer.trigger_time >= timer.how_long:

            timers[index].procedure()
            
            timers[index].discountCycle()

            timers[index].trigger_time = tm()