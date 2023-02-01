import timer

tm1 = timer.Timer(1, lambda: print('tm1'), True) 
tm2 = timer.Timer(3.5, lambda: print('tm2'), True) 
tm3 = timer.Timer(1.5, lambda: print('tm3'), False) 

while True:

    timer.updateTimers([tm1,tm2,tm3])