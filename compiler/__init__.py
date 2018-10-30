from enum import Enum

# implemented in Nim/lib/system.nim
FileMode = Enum("FileMode", ["fmRead", "fmWrite",
                             "fmReadWrite", "fmReadWriteExisting", "fmAppend"])
