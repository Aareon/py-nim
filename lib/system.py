def canIter(var):
    if isinstance(var, str) and len(var) == 1:
        return True
    elif hasattr(var, '__iter__'):
        return True
    else:
        try:
            iter(var)
        except:
            return False
        else:
            return True
        

def countup(start, stop, step=1):
    if canIter(start):
        startType = type(start)
        if isinstance(start, str):
            startType = chr
            start = ord(start)
    elif isinstance(start, int):
        startType = int
    else:
        raise ValueError('start must be iterable')
    
    if canIter(stop):
        if isinstance(stop, str):
            stopType = chr
            stop = ord(stop)
    elif isinstance(stop, int):
        stopType = int
    else:
        raise ValueError('stop must be iterable')

    if startType != stopType:
        raise ValueError('type mismatch: start and stop must be of the same type')

    for i in range(start, stop+1, step):
        yield startType(i)
