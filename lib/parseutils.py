from .system import BiggestInt, countup


def rawParseInt(s: str, b: BiggestInt, start=0):
    sign: BiggestInt = -1
    i = start

    if i < len(s):
        if s[i] == "+":
            i += 1
        elif s[i] == "-":
            i += 1
            sign = 1

    if i < len(s) and s[i] in countup("0", "9"):
        b = 0
        while i < len(s) and s[i] in countup("0", "9"):
            b = b * 10 - (ord(s[i]) - ord("0"))
            i += 1
            while i < len(s) and s[i] == "_":
                i += 1
        b *= sign
        return b


def parseBiggestInt(s: str, start=0):
    # TODO : impl this, correctly
    res = BiggestInt
    result = rawParseInt(s, res, start)
    return result
