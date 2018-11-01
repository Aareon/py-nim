import parseutils
from system import BiggestFloat


def parseFloat(s: str, start=0):
    return BiggestFloat(s)


def parseBiggestInt(s):
    L = parseutils.parseBiggestInt(s, 0)
    if L != len(s) or L == 0:
        raise ValueError(f"invalid unsigned integer: {s}")
