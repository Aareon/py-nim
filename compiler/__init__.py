from enum import Enum
from lib.system import *

# implemented in Nim/lib/system.nim
FileMode = Enum("FileMode", ["fmRead", "fmWrite",
                             "fmReadWrite", "fmReadWriteExisting", "fmAppend"])
