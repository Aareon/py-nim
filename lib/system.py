from enum import Enum

int8 = type("int8", (int,), {"high": 0x7F, "low": -0x80})
int16 = type("int16", (int,), {"high": 0x7FFF, "low": -0x8000})
int32 = type("int32", (int,), {"high": 0x7FFFFFFF, "low": -0x80000000})
int64 = type("int64", (int,), {"high": 0x7FFFFFFFFFFFFFFF, "low": -0x8000000000000000})
uint8 = type("uint8", (int,), {"high": 0xFF, "low": 0x0})
uint16 = type("uint16", (int,), {"high": 0xFFFF, "low": 0x0})
uint32 = type("uint32", (int,), {"high": 0xFFFFFFFF, "low": 0x0})

BiggestInt = int64

float32 = type("float32", (float,), {"high": "inf"})
float64 = type("float64", (float,), {"high": "inf"})
float128 = type("float128", (float,), {"high": "inf"})

BiggestFloat = float64

string = type(
    "string",
    (str,),
    {
        "_len": None,
        "len": property(lambda self: self._len if self._len is not None else len(self)),
        "setLen": lambda self, n: setLen(self, n),
        "__str__": lambda self: self[0: self.len],
        "__repr__": lambda self: f"'{self.__str__()}'",  # used for debugging
    },
)


def high(x):
    if hasattr(x, "high"):
        return x.high


def low(x):
    if hasattr(x, "low"):
        return x.low


def toU8(x: int):
    return uint8(x)


def toU16(x: int):
    return uint16(x)


def toU32(x: int):
    return uint32(x)


def countup(start, stop, step=1):
    def canIter(var):
        if isinstance(var, str) and len(var) == 1:
            return True
        elif hasattr(var, "__iter__"):
            return True
        else:
            try:
                iter(var)
            except:
                return False
            else:
                return True

    if canIter(start):
        startType = type(start)
        if isinstance(start, str):
            startType = chr
            start = ord(start)
    elif isinstance(start, int):
        startType = int
    else:
        raise ValueError("start must be iterable")

    if canIter(stop):
        if isinstance(stop, str):
            stopType = chr
            stop = ord(stop)
    elif isinstance(stop, int):
        stopType = int
    else:
        raise ValueError("stop must be iterable")

    if startType != stopType:
        raise ValueError("type mismatch: start and stop must be of the same type")

    for i in range(start, stop + 1, step):
        yield startType(i)


FileMode = Enum(
    "FileMode", ["fmRead", "fmWrite", "fmReadWrite", "fmReadWriteExisting", "fmAppend"]
)


def setLen(x, n):
    if not isinstance(n, int):
        raise ValueError(f"expected 'int', got 'type({n})'")
    if n < 0:
        raise ValueError(f"value {n} is not a natural number")
    if hasattr(x, "_len") and hasattr(x, "len"):
        x._len = n
