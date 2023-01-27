from time import time as tm

class Timer():

    class pausedDeactivatedClock(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
    class unpausedDeactivatedClock(AssertionError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
    
    def __eq__(self, __o: object) -> bool:
        if type(self) == type(__o) and self.id == __o.id:
            return True
        return False

    def __init__(self, howLong: float, procedure: callable, once: bool) -> None:
        '''Creates a timer instance.\n
           howLong: the amount of time for the timer.\n
           procedure: the method to be called after the timer completes a cycle.\n
           once: bool to define if the timer is going to be repeatedly cycling or not.\n'''

        self.trigger_time = tm()
        self.how_long = howLong
        self.procedure = procedure
        self.once = once

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

    def destroyTimer(self) -> None:
        '''Timer will be destroyed and won't conclude any other time.\n'''

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
       If the timer is defined to work only once, deletes the timer from the list if it completes the first cycle.\n'''
    
    for timer in timers:

        if not timer.activated:
            continue

        if timer.destroyed:
            timers.remove(timer)
            continue

        if tm() - timer.trigger_time >= timer.how_long:

            timer.procedure()
            
            if timer.once: timers.remove(timer)

            timer.trigger_time = tm()